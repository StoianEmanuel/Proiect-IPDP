import unittest
from meta_method import get_all_tables, get_column_data

class TestFunctions(unittest.TestCase):

    def test_get_column_data(self):
        # Get column data from the TestTable
        column_data = get_column_data("./Data/gaming.sqlite", "TestTable")
        self.assertEqual(column_data, '')
    
    def test_get_column_data_0(self):
    # Get column data from a custom table in a custom database
        db_path = "./Data/gaming.sqlite"
        table_name = "Consoles"
        column_data = get_column_data(db_path, table_name)
        self.assertEqual(column_data, "Id,Name,Manufacturer,Release Year,Units Sold (millions),Type,Number of Exclusives,Processing Unit Type,CPU Equivalent,CPU Frequency,GPU Equivalent,RAM Size,RAM Frequency,Launch Price ($)")

    def test_get_column_data_1(self):
    # Get column data from a custom table in a custom database
        db_path = "./Data/gaming.sqlite"
        table_name = "VideoGames"
        column_data = get_column_data(db_path, table_name)
        self.assertEqual(column_data, "Id,Name,Platform,Release Year,Genre,Publisher,North America Sales,Europe Sales,Japan Sales,Other Sales,Global Sales,Critic Score,Critic Count,User Score,User Count,Developer,Rating")
	
    def test_get_column_data_2(self):
    # Get column data from a custom table in a custom database
        db_path = "./Data/gaming.sqlite"
        table_name = "Mice"
        column_data = get_column_data(db_path, table_name)
        self.assertEqual(column_data, "Id,Manufacturer,Model,Resolution,Design,Number of buttons,Interface,Weight,Size,Rating,Link address,Battery,Use,Extra Functions")
	
    def test_get_column_data_3(self):
    # Get column data from a custom table in a custom database
        db_path = "./Data/gaming.sqlite"
        table_name = "CPU"
        column_data = get_column_data(db_path, table_name)
        self.assertEqual(column_data, "Model,Manufacturer,Family,Codename,Release Year,Discontinued,Base Clock,Boost Clock,Sockets,L1 Cache Size,L2 Cache Size,Process Size (nm),Number of Cores,Number of Threads,TDP,System Memory Type,System Memory Frequency,Instruction Set,Maximum Operating Temperature,Launch Price ($)")
	
    def test_get_column_data_4(self):
    # Get column data from a custom table in a custom database
        db_path = "./Data/gaming.sqlite"
        table_name = "GPU"
        column_data = get_column_data(db_path, table_name)
        self.assertEqual(column_data, "Model,Manufacturer,Release Year,Discontinued,Graphics Processor,Transistors (millions),Process Size (nm),Integration Density,Shading Units,Core Base Clock,Core Boost Clock,Memory Type,Memory Size,Memory Bandwidth,Memory Clock Speed (Effective),TDP,Display Outputs,Cooling System,Cooling Type,DirectX,OpenGL,OpenCL,Vulkan,Shader Model,CUDA,Launch Price ($)")

if __name__ == '__main__':
    unittest.main()