import vtk

# 定义输入VTP文件路径和文件名
path = "Dataset/MedModels/0014_H_AO_COA/Models/"
input_filename = "0102_0001.vtp"

output_filename = input_filename[:-4] + ".stl"

# 创建VTP文件读取器
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(path + input_filename)
reader.Update()

# 创建STL文件写入器
stl_writer = vtk.vtkSTLWriter()
stl_writer.SetFileName(path + output_filename)
stl_writer.SetInputData(reader.GetOutput())
stl_writer.Write()