from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *

import os
import json
import random

import cv2
import numpy as np
from modelscope import snapshot_download
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file


class FaceRecognitionPumping(QWidget):
    """人脸检测抽人界面
    
    集成人脸检测功能的课堂点名系统，支持实时摄像头画面显示、
    人脸检测、动态圈圈随机移动等功能。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("face_recognition_pumpingInterface")
        
        # 初始化变量并设置默认值
        self.is_animating = False
        self.animation_timer = None
        self.circle_timer = None
        self.camera = None
        self.face_detector = None
        self.detected_faces = []
        self.current_circle_pos = None
        self.selected_student = None
        self.models_loaded = False
        self.frame_count = 0  # 帧计数器，用于控制人脸检测频率
        
        # 优化显示分辨率设置
        self.display_width = 1280  # 更合理的默认显示宽度
        self.display_height = 720   # 更合理的默认显示高度
        
        # 添加性能监控变量
        self.last_frame_time = 0
        self.frame_rate = 0
        
        # 初始化UI
        self.initUI()
        
        # 加载人脸识别模型
        self.load_face_models()
        
    def initUI(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = TitleLabel("人脸检测抽人系统")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 摄像头显示区域
        self.camera_label = BodyLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.camera_label)
        
        # 控制面板
        control_panel = QHBoxLayout()
        
        # 开启摄像头按钮
        self.camera_button = PrimaryPushButton("开启摄像头")
        self.camera_button.setFixedSize(120, 40)
        self.camera_button.setFont(QFont(load_custom_font(), 12))
        self.camera_button.clicked.connect(self.toggle_camera)
        control_panel.addWidget(self.camera_button)
        
        # 抽取按钮
        self.start_button = PushButton("开始抽取")
        self.start_button.setFixedSize(120, 40)
        self.start_button.setFont(QFont(load_custom_font(), 12))
        self.start_button.clicked.connect(self.start_face_pumping)
        self.start_button.setEnabled(False)
        control_panel.addWidget(self.start_button)
        
        # 全屏按钮
        self.fullscreen_button = PushButton("全屏显示")
        self.fullscreen_button.setFixedSize(120, 40)
        self.fullscreen_button.setFont(QFont(load_custom_font(), 12))
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        control_panel.addWidget(self.fullscreen_button)
        
        control_panel.addStretch()
        main_layout.addLayout(control_panel)
        
        # 状态显示
        self.status_label = BodyLabel("状态：等待开启摄像头")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 结果显示区域
        result_group = QGroupBox("抽取结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_label = BodyLabel("等待抽取...")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont(load_custom_font(), 16))
        result_layout.addWidget(self.result_label)
        
        main_layout.addWidget(result_group)
        
        # 添加弹性空间
        main_layout.addStretch()
        
    def load_face_models(self):
        """加载人脸检测模型"""
        try:
            self.status_label.setText("状态：正在加载人脸检测模型...")

            # 指定要下载的模型
            model_name = 'iic/cv_manual_face-detection_ulfd'
            
            # 获取模型保存目录，添加空值检查
            model_save_dir = path_manager.get_resource_path("assets/face_models", f"{model_name}")
            if model_save_dir is None:
                raise Exception("无法获取模型保存目录路径")
            
            # 确保目录存在
            try:
                os.makedirs(model_save_dir, exist_ok=True)
            except Exception as dir_error:
                logger.error(f"创建模型目录失败: {dir_error}")
                raise Exception(f"创建模型目录失败: {dir_error}")
            
            # 检查模型是否已存在
            if os.path.exists(model_save_dir) and os.listdir(model_save_dir):
                logger.info(f"检测到本地模型目录存在: {model_save_dir}")
                self.status_label.setText("状态：检测到本地模型，正在加载...")
                # 使用字符串路径，避免WindowsPath对象问题
                model_dir = str(model_save_dir)
            
            # 验证模型目录
            if model_dir is None:
                raise Exception("模型目录路径为空")
            
            # 使用本地模型路径初始化pipeline
            self.status_label.setText("状态：正在初始化模型...")
            try:
                # 确保model_dir是有效路径
                if not os.path.exists(model_dir):
                    raise Exception(f"模型目录不存在: {model_dir}")
                    
                # 初始化pipeline并验证
                self.face_detector = pipeline(Tasks.face_detection, model=model_dir)
                
                # 严格验证pipeline是否成功初始化
                if self.face_detector is None:
                    raise Exception("人脸检测器初始化失败，返回None")
                if not hasattr(self.face_detector, '__call__'):
                    raise Exception("初始化的人脸检测器不可调用")
                    
            except Exception as init_error:
                logger.error(f"本地模型初始化失败: {init_error}")
            
            self.models_loaded = True
            self.status_label.setText("状态：人脸检测模型加载完成")
            logger.info("人脸检测模型加载完成")
            
        except Exception as e:
            logger.error(f"加载人脸检测模型失败: {e}")
            self.status_label.setText(f"状态：模型加载失败 - {str(e)}")
            # 确保在失败时重置所有相关状态
            self.models_loaded = False
            self.face_detector = None
            # 确保detected_faces是有效的列表
            if self.detected_faces is None:
                self.detected_faces = []
            elif not isinstance(self.detected_faces, list):
                logger.warning(f"detected_faces类型错误: {type(self.detected_faces)}，重置为空列表")
                self.detected_faces = []
            else:
                self.detected_faces.clear()
            
    def toggle_camera(self):
        """切换摄像头状态"""
        if self.camera is None:
            self.start_camera()
        else:
            self.stop_camera()
            
    def start_camera(self):
        """开启摄像头"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("无法开启摄像头")
                
            # 设置摄像头分辨率，降低数据量提高性能
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.display_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.display_height)
            
            self.camera_button.setText("关闭摄像头")
            self.start_button.setEnabled(True)
            self.status_label.setText("状态：摄像头已开启")
            
            # 启动摄像头更新定时器
            self.camera_timer = QTimer()
            self.camera_timer.timeout.connect(self.update_camera_frame)
            self.camera_timer.start(5)
            
            logger.info("摄像头已开启")
            
        except Exception as e:
            logger.error(f"开启摄像头失败: {e}")
            self.status_label.setText(f"状态：摄像头开启失败 - {str(e)}")
            
    def stop_camera(self):
        """安全关闭摄像头并释放资源"""
        try:
            # 释放摄像头资源
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                
            # 停止所有定时器
            for timer_name in ['camera_timer', 'circle_timer', 'animation_timer']:
                if hasattr(self, timer_name):
                    timer = getattr(self, timer_name)
                    if timer is not None and timer.isActive():
                        timer.stop()
                        setattr(self, timer_name, None)
            
            # 重置UI状态
            self.camera_button.setText("开启摄像头")
            self.start_button.setEnabled(False)
            self.status_label.setText("状态：摄像头已关闭")
            self.camera_label.clear()
            
            # 重置动画状态
            self.is_animating = False
            self.current_circle_pos = None
            
            logger.info("摄像头已安全关闭并释放所有资源")
        except Exception as e:
            logger.error(f"关闭摄像头时发生错误: {e}")
            self.status_label.setText(f"状态：关闭摄像头时出错 - {str(e)}")
        
    def update_camera_frame(self):
        """更新摄像头画面"""
        if self.camera is None or not self.camera.isOpened():
            return
            
        ret, frame = self.camera.read()
        if not ret:
            return
            
        # 帧计数器递增
        self.frame_count += 1
        
        # 创建透明图层用于绘制人脸框
        if not hasattr(self, 'overlay_layer'):
            self.overlay_layer = np.zeros_like(frame)
            
        # 清空上一帧的绘制
        self.overlay_layer.fill(0)
        
        # 优化人脸检测频率和性能
        if self.models_loaded:
            # 使用更快的插值方法并适当降低分辨率
            detection_frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_NEAREST)
            
            # 执行人脸检测
            result = self.face_detector(detection_frame)
            
            # 处理检测结果
            if result and 'boxes' in result:
                # 计算缩放比例
                scale_x = frame.shape[1] / detection_frame.shape[1]
                scale_y = frame.shape[0] / detection_frame.shape[0]
                
                # 处理每个人脸框
                for box in result['boxes']:
                    if box is not None and len(box) >= 4:
                        x1, y1, x2, y2 = map(int, box[:4])
                        x1 = int(x1 * scale_x)
                        y1 = int(y1 * scale_y)
                        x2 = int(x2 * scale_x)
                        y2 = int(y2 * scale_y)
                        
                        # 在透明图层上绘制人脸框
                        cv2.rectangle(self.overlay_layer, (x1, y1), (x2, y2), (0, 255, 0), 2)
            else:
                # 没有检测到人脸时清空图层
                self.overlay_layer.fill(0)
                        
        # 合并原始帧和透明图层
        frame = cv2.addWeighted(frame, 1, self.overlay_layer, 1, 0)
        
        # 绘制动态圈圈
        if self.is_animating and self.current_circle_pos:
            self.draw_circle(frame)
        
        # 优化图像显示性能
        if frame.size > 0:  # 确保帧有效
            # 使用更高效的颜色空间转换
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 直接创建QPixmap避免中间QImage对象
            pixmap = QPixmap.fromImage(
                QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], 
                       rgb_frame.shape[1] * 3, QImage.Format_RGB888)
            )
            
            # 使用平滑变换保持质量
            self.camera_label.setPixmap(
                pixmap.scaled(self.camera_label.size(), 
                             Qt.KeepAspectRatio, 
                             Qt.SmoothTransformation)
            )
        
    def detect_faces(self, detection_frame, display_frame):
        """
        检测并处理人脸
        
        参数:
            detection_frame: 用于检测的低分辨率帧
            display_frame: 用于显示的高分辨率帧
        """
        if not self._validate_detection_inputs(detection_frame, display_frame):
            return
            
        # 执行人脸检测
        result = self.face_detector(detection_frame)
        
        # 清空之前检测到的人脸
        self._reset_detected_faces()
        
        # 处理检测结果
        if not self._validate_detection_result(result):
            return
            
        # 计算缩放比例
        scale_x, scale_y = self._calculate_scale_factors(detection_frame, display_frame)
        if scale_x is None or scale_y is None:
            return
            
        # 处理每个人脸框
        boxes = result['boxes']
        for i, box in enumerate(boxes):
            face_coords = self._process_single_face(box, i, scale_x, scale_y, display_frame)
            if face_coords:
                self.detected_faces.append(face_coords)
                
    def _validate_detection_inputs(self, detection_frame, display_frame):
        """验证输入帧的有效性"""
        if self.face_detector is None:
            logger.warning("人脸检测器未初始化")
            return False
            
        if detection_frame is None or display_frame is None:
            logger.warning("输入帧为空")
            return False
            
        return True
        
    def _reset_detected_faces(self):
        """重置检测到的人脸列表"""
        if self.detected_faces is None:
            self.detected_faces = []
        elif not isinstance(self.detected_faces, list):
            logger.warning(f"detected_faces类型错误: {type(self.detected_faces)}，重置为空列表")
            self.detected_faces = []
        else:
            self.detected_faces.clear()
            
    def _validate_detection_result(self, result):
        """验证检测结果的有效性"""
        if result is None:
            logger.warning("人脸检测结果为空")
            return False
            
        if not isinstance(result, dict):
            logger.warning(f"人脸检测结果格式错误，期望字典类型，实际类型: {type(result)}")
            return False
            
        if 'boxes' not in result:
            logger.warning("人脸检测结果中缺少'boxes'字段")
            return False
            
        boxes = result['boxes']
        if boxes is None:
            logger.warning("人脸检测结果中boxes为空")
            return False
            
        if not isinstance(boxes, (list, tuple)):
            logger.warning(f"boxes格式错误，期望列表或元组，实际类型: {type(boxes)}")
            return False
            
        return True
        
    def _calculate_scale_factors(self, detection_frame, display_frame):
        """计算检测帧到显示帧的缩放比例"""
        try:
            scale_x = display_frame.shape[1] / detection_frame.shape[1]
            scale_y = display_frame.shape[0] / detection_frame.shape[0]
            return scale_x, scale_y
        except (ZeroDivisionError, IndexError) as scale_error:
            logger.error(f"计算缩放比例失败: {scale_error}")
            return None, None
            
    def _process_single_face(self, box, index, scale_x, scale_y, display_frame):
        """处理单个人脸框"""
        try:
            # 验证人脸框数据
            if box is None:
                logger.warning(f"第{index}个人脸框为空")
                return None
                
            if not isinstance(box, (list, tuple, np.ndarray)):
                logger.warning(f"第{index}个人脸框格式错误，类型: {type(box)}")
                return None
                
            if len(box) < 4:
                logger.warning(f"第{index}个人脸框数据不足，长度: {len(box)}")
                return None
                
            # 计算并验证坐标
            x1, y1, x2, y2 = map(int, box[:4])
            x1 = int(x1 * scale_x)
            y1 = int(y1 * scale_y)
            x2 = int(x2 * scale_x)
            y2 = int(y2 * scale_y)
            
            if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
                logger.warning(f"第{index}个人脸框坐标无效: ({x1}, {y1}) - ({x2}, {y2})")
                return None
                
            # 绘制人脸框并确保显示
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 立即更新显示帧
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            pixmap = QPixmap.fromImage(
                QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], 
                       rgb_frame.shape[1] * 3, QImage.Format_RGB888)
            )
            self.camera_label.setPixmap(
                pixmap.scaled(self.camera_label.size(), 
                             Qt.KeepAspectRatio, 
                             Qt.SmoothTransformation)
            )
            QApplication.processEvents()
            
            return (x1, y1, x2, y2)
            
        except Exception as e:
            logger.error(f"处理第{index}个人脸框时出错: {e}")
            return None
            
    def draw_circle(self, frame):
        """在画面中绘制动态圈圈"""
        if self.current_circle_pos:
            x, y = self.current_circle_pos
            cv2.circle(frame, (x, y), 50, (0, 0, 255), 3)
            
    def start_face_pumping(self):
        """开始人脸检测抽人"""
        # 检查检测到的人脸列表是否有效
        if self.detected_faces is None:
            logger.warning("检测到的人脸列表为None，重置为空列表")
            self.detected_faces = []
            self.status_label.setText("状态：未检测到人脸")
            return
            
        if not isinstance(self.detected_faces, (list, tuple)):
            logger.warning(f"检测到的人脸列表格式错误，类型: {type(self.detected_faces)}，重置为空列表")
            self.detected_faces = []
            self.status_label.setText("状态：未检测到人脸")
            return
            
        if len(self.detected_faces) == 0:
            self.status_label.setText("状态：未检测到人脸")
            return
            
        if self.is_animating:
            self.stop_face_pumping()
        else:
            self.start_button.setText("停止抽取")
            self.is_animating = True
            
            # 启动圈圈动画
            try:
                self.circle_timer = QTimer()
                self.circle_timer.timeout.connect(self.update_circle_position)
                self.circle_timer.start(100)  # 每100ms更新一次位置
            except Exception as timer_error:
                logger.error(f"创建圈圈动画定时器失败: {timer_error}")
                self.is_animating = False
                self.start_button.setText("开始抽取")
                return
            
            # 设置自动停止时间（例如5秒后）
            try:
                QTimer.singleShot(5000, self.stop_face_pumping)
            except Exception as single_shot_error:
                logger.error(f"设置自动停止时间失败: {single_shot_error}")
            
            self.status_label.setText("状态：正在抽取...")
            
    def stop_face_pumping(self):
        """停止人脸检测抽人"""
        self.is_animating = False
        self.start_button.setText("开始抽取")
        
        if hasattr(self, 'circle_timer'):
            try:
                self.circle_timer.stop()
            except Exception as timer_stop_error:
                logger.error(f"停止圈圈动画定时器失败: {timer_stop_error}")
            
        # 选择最终结果
        if self.detected_faces is None:
            logger.warning("检测到的人脸列表为None，重置为空列表")
            self.detected_faces = []
            self.status_label.setText("状态：抽取失败")
            return
            
        if not isinstance(self.detected_faces, (list, tuple)):
            logger.warning(f"检测到的人脸列表格式错误，类型: {type(self.detected_faces)}，重置为空列表")
            self.detected_faces = []
            self.status_label.setText("状态：抽取失败")
            return
            
        if len(self.detected_faces) > 0:
            try:
                selected_face = random.choice(self.detected_faces)
                
                # 检查选中的人脸数据是否有效
                if selected_face is None:
                    logger.warning("随机选择的人脸为None")
                    self.status_label.setText("状态：抽取失败")
                    return
                    
                if not isinstance(selected_face, (list, tuple)):
                    logger.warning(f"选中的人脸格式错误，类型: {type(selected_face)}")
                    self.status_label.setText("状态：抽取失败")
                    return
                    
                if len(selected_face) < 4:
                    logger.warning(f"选中的人脸数据不足，长度: {len(selected_face)}")
                    self.status_label.setText("状态：抽取失败")
                    return
                
                self.selected_student = selected_face
                
                # 显示结果
                try:
                    x1, y1, x2, y2 = map(int, selected_face[:4])
                    self.result_label.setText(f"已选中学生！位置：({x1}, {y1}) - ({x2}, {y2})")
                    self.status_label.setText("状态：抽取完成")
                    
                    # 在选中的人脸周围绘制高亮框
                    self.current_circle_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
                except Exception as display_error:
                    logger.error(f"显示抽取结果失败: {display_error}")
                    self.status_label.setText("状态：抽取结果显示失败")
                    
            except Exception as choice_error:
                logger.error(f"选择人脸失败: {choice_error}")
                self.status_label.setText("状态：抽取失败")
        else:
            self.status_label.setText("状态：未检测到人脸")
            
    def update_circle_position(self):
        """更新圈圈位置"""
        # 检查检测到的人脸列表是否有效
        if self.detected_faces is None:
            logger.warning("检测到的人脸列表为None，重置为空列表")
            self.detected_faces = []
            return
            
        if not isinstance(self.detected_faces, (list, tuple)):
            logger.warning(f"检测到的人脸列表格式错误，类型: {type(self.detected_faces)}，重置为空列表")
            self.detected_faces = []
            return
            
        if len(self.detected_faces) > 0:
            try:
                # 随机选择一个人脸位置
                selected_face = random.choice(self.detected_faces)
                
                # 检查选中的人脸数据是否有效
                if selected_face is None:
                    logger.warning("随机选择的人脸为None")
                    return
                    
                if not isinstance(selected_face, (list, tuple)):
                    logger.warning(f"选中的人脸格式错误，类型: {type(selected_face)}")
                    return
                    
                if len(selected_face) < 4:
                    logger.warning(f"选中的人脸数据不足，长度: {len(selected_face)}")
                    return
                
                # 计算圈圈位置
                x1, y1, x2, y2 = map(int, selected_face[:4])
                self.current_circle_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
                
            except Exception as position_error:
                logger.error(f"更新圈圈位置失败: {position_error}")
                # 出错时清除圈圈位置
                self.current_circle_pos = None
            
    def toggle_fullscreen(self):
        """切换全屏显示"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_button.setText("全屏显示")
        else:
            self.showFullScreen()
            self.fullscreen_button.setText("退出全屏")
            
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        self.stop_camera()
        super().closeEvent(event)