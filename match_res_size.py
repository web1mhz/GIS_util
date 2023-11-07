
'''
conda activate geo38

'''

import sys
import os
import numpy as np
import rasterio
import glob
from rasterio.warp import reproject, Resampling
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget

class RasterReprojectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Raster Reprojection Tool")
        self.setGeometry(100, 100, 800, 600)

        self.reference_raster = None
        self.target_raster = None

        self.init_ui_components()
        
    def init_ui_components(self):
        # 레이블
        self.label_reference = QLabel("Reference Raster:")
        self.label_target = QLabel("Target Raster:")
        self.label_target_folder = QLabel("Target Raster folder:")

        # 파일 선택 버튼
        self.btn_reference = QPushButton("Select Reference Raster")
        self.btn_target = QPushButton("Select Target Raster")
        self.btn_modified_target_save_folder = QPushButton("Select modified Target Raster folder")

        # 재투영 버튼
        self.btn_reproject = QPushButton("Reproject")

        # 버튼 클릭 이벤트 연결
        self.btn_reference.clicked.connect(self.select_reference_raster)
        self.btn_target.clicked.connect(self.select_target_raster)
        self.btn_modified_target_save_folder.clicked.connect(self.modified_target_raster_folder)

        self.btn_reproject.clicked.connect(self.reproject_rasters)
        

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.label_reference)
        layout.addWidget(self.btn_reference)
        layout.addWidget(self.label_target)
        layout.addWidget(self.btn_target)

        layout.addWidget(self.label_target_folder)
        layout.addWidget(self.btn_modified_target_save_folder)

        layout.addWidget(self.btn_reproject)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def select_reference_raster(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("TIF Files (*.tif)")
        if file_dialog.exec_():
            self.reference_raster = file_dialog.selectedFiles()[0]
            self.label_reference.setText("Reference Raster: " + self.reference_raster)

    def select_target_raster(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("TIF Files (*.tif)")
        if file_dialog.exec_():
            self.target_raster = file_dialog.selectedFiles()[0]
            self.label_target.setText("Target Raster: " + self.target_raster)  

    def modified_target_raster_folder(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setNameFilter("TIF Files (*.tif)")
        if folder_dialog.exec_():
            self.output_folder = folder_dialog.selectedFiles()[0]
            self.label_target_folder.setText("Target Raster save folder: " +self.output_folder)                        

    def select_target_raster_folder(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setNameFilter("TIF Files (*.tif)")
        if folder_dialog.exec_():
            self.output_folder = folder_dialog.selectedFiles()[0]
            self.label_target_folder.setText("Target Raster save folder: " +self.output_folder)             


    def reproject_rasters(self):

        raseter_name = os.path.basename(self.target_raster).split('.')[0]        
        
        if self.reference_raster and self.target_raster:
            with rasterio.open(self.reference_raster) as src_ref:
                reference_resolution = src_ref.res
                reference_extent = src_ref.bounds
                reference_crs = src_ref.crs

                with rasterio.open(self.target_raster) as src_target:
                    target_resolution = src_target.res
                    target_extent = src_target.bounds
                    target_crs = src_target.crs

                    reprojected_data, _ = reproject(
                        source=rasterio.band(src_target, 1),
                        destination=np.empty((src_ref.height, src_ref.width)),
                        src_transform=src_target.transform,
                        src_crs=target_crs,
                        src_resolution=target_resolution,
                        dst_transform=src_ref.transform,
                        dst_crs=reference_crs,
                        dst_resolution=reference_resolution,
                        resampling=Resampling.bilinear
                    )
                    

                    # 사용자가 선택한 폴더 내에 파일 저장
                    output_raster = os.path.join(self.output_folder, f"{raseter_name}_ed.tif")
                    print(output_raster)
                    # output_raster = "output_raster.tif"
                    with rasterio.open(output_raster, 'w', driver='GTiff', width=reprojected_data.shape[1],
                                    height=reprojected_data.shape[0], count=1, dtype=reprojected_data.dtype,
                                    crs=reference_crs, transform=src_ref.transform) as dst:
                        dst.write(reprojected_data, 1)

                    self.label_reference.setText("Reference Raster: " + self.reference_raster)
                    self.label_target.setText("Target Raster: " + self.target_raster)
                    print(f"해상도 및 지리적 범위가 일치하는 래스터 파일이 생성되었습니다.")

    
    
    def reproject_rasters_folder(self):

        print("선택됨", f"{self.output_folder}")

        tif_list = glob.glob(f"{self.output_folder}/*.tif")

        for tif in tif_list:
            self.reproject_rasters(tif)
            print(tif)

        

def main():
    app = QApplication(sys.argv)
    window = RasterReprojectionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
