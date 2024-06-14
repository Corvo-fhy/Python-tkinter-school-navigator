# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Menu, Text, Scrollbar
import geopandas as gpd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import Point
from matplotlib_scalebar.scalebar import ScaleBar



class ImageGallery:
    def __init__(self, root):
        self.root = root
        self.image_paths = ["sence1.jpg", "sence2.jpg", "sence3.jpg", "sence4.jpg"]  # 替换为你的图片路径
        self.current_image_index = 0

        self.image_window = tk.Toplevel(root)
        self.image_window.title("特色场景")

        self.img_label = tk.Label(self.image_window)
        self.img_label.pack()

        self.prev_button = tk.Button(self.image_window, text="上一张", command=self.show_prev_image)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.image_window, text="下一张", command=self.show_next_image)
        self.next_button.pack(side=tk.RIGHT)

        self.show_image()

    def show_image(self):
        img = Image.open(self.image_paths[self.current_image_index])
        img = img.resize((800, 600), Image.ANTIALIAS)
        self.img_photo = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.img_photo)
        self.img_label.image = self.img_photo  # 保持引用

    def show_prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_image()

    def show_next_image(self):
        if self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.show_image()

def show_images():
    ImageGallery(root)




# 创建主窗口
root = tk.Tk()
root.title("内蒙古财经大学导览系统")
root.geometry("1024x768")

# 设置背景图片
background_image = Image.open("background.jpg")  # 替换为你的背景图片路径
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# 创建菜单
menu = Menu(root)
root.config(menu=menu)


def parse_geographic_data():
    # 从 GeoJSON 文件中读取地理数据并解析
    try:
        gdf = gpd.read_file('data.geojson')

        # 分离不同的几何类型
        points = gdf[gdf.geometry.type == 'Point']
        lines = gdf[gdf.geometry.type == 'LineString']
        polygons = gdf[gdf.geometry.type == 'Polygon']

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号显示为方块的问题

        # 设置保存文件夹路径
        output_folder = 'output_shapefiles'
        os.makedirs(output_folder, exist_ok=True)  # 创建保存文件夹，如果不存在则创建

        # 设置绘图区域
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # 分别绘制不同几何类型，并设置颜色
        if not points.empty:
            points.plot(ax=ax, marker='o', color='blue', markersize=5, label='Points')
        if not lines.empty:
            lines.plot(ax=ax, color='green', linewidth=2, label='道路')
        if not polygons.empty:
            polygons.plot(ax=ax, edgecolor='k', facecolor='orange', alpha=0.5, label='建筑及学校占地')

        # 手动创建图例并确保颜色正确
        legend_elements = [
            Patch(facecolor='green', edgecolor='black', label='道路'),
            Patch(facecolor='orange', edgecolor='black', alpha=1, label='建筑及学校占地')
        ]

        # 设置图例
        ax.legend(handles=legend_elements, loc='upper left')

        # 设置横纵轴的标签格式为十进制
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))

        # 添加比例尺
        scalebar = ScaleBar(1000, location='lower right')
        ax.add_artist(scalebar)

        # 添加指北针
        x, y, arrow_length = 0.95, 0.95, 0.1
        ax.annotate('N',
                    xy=(x, y), xytext=(x, y - arrow_length),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=12,
                    xycoords=ax.transAxes)


        # 设置标题
        ax.set_title('基于GeoJSON的内蒙古财经大学可视化地图')
        plt.savefig('map.png')  # 保存为 PNG 格式的文件
        # 显示绘图
        plt.show()

        # 保存为Shapefile文件
        if not points.empty:
            points.to_file(os.path.join(output_folder, 'points_shapefile.shp'), driver='ESRI Shapefile')
        if not lines.empty:
            lines.to_file(os.path.join(output_folder, 'lines_shapefile.shp'), driver='ESRI Shapefile')
        if not polygons.empty:
            polygons.to_file(os.path.join(output_folder, 'polygons_shapefile.shp'), driver='ESRI Shapefile')

        print(f"Shapefiles saved in {output_folder} folder.")

    except Exception as e:
        messagebox.showerror("错误", f"无法解析地理要素: {e}")


def open_shapefile():
    file_path = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
    if file_path:
        try:
            gdf = gpd.read_file(file_path)
            display_shapefile_content(gdf)
            print(gdf)
            messagebox.showinfo("信息", f"已打开 Shapefile 文件: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 Shapefile 文件: {e}")


def display_shapefile_content(gdf):
    content_window = tk.Toplevel(root)
    content_window.title("Shapefile 内容")

    text = Text(content_window, wrap="none")
    text.pack(expand=True, fill="both")

    scrollbar_y = Scrollbar(content_window, orient="vertical", command=text.yview)
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = Scrollbar(content_window, orient="horizontal", command=text.xview)
    scrollbar_x.pack(side="bottom", fill="x")

    text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    text.insert("end", gdf.to_string())


def show_school_info():
    info = ("内蒙古财经大学坐落于首府呼和浩特市。是一所承载历史使命，富有创新精神的高等学府。学校始建于1960年，时名为内蒙古财经学院，1962年改建为内蒙古财贸干部进修学院，1965年改建为内蒙古财贸学校，1979"
            "年恢复本科招生，1980年经国务院批准复建内蒙古财经学院，2000年与内蒙古经济管理干部学院合并，2006年内蒙古财税职业学院、工商行政管理学校并入。2012年经教育部批准，学校更名为内蒙古财经大学。经过60"
            "余年的建设与发展，现已成为一所以本科和研究生教育为主、同时承担高等职业教育、继续教育培养任务，以经济学和管理学为主，理学、法学、工学、文学融合发展，具有鲜明财经特色的多科性应用型大学。\n"
            "学校以铸牢中华民族共同体意识教育为主线，秉承“崇德、尚学、明理、包容”的校训，坚持“育人为本、质量立校、人才强校、依法治校”的办学理念，坚持“以本为本”，推进“四个回归”，创新“传承财经本色、强化融合底色、打造数字特色”人才培养理念，推动经济学、管理学、理学、法学、工学、文学多学科交叉融合与协调发展。构建“专、数、创”交叉融合的特色学科专业体系，推进“五育并举”“三全育人”，面向国家重大战略和重大需求，聚焦更好服务自治区五大任务，优化调整学科专业布局，培养具有家国情怀、创新精神、创业素质的应用型复合型数智化新财经人才。\n"
            "学校学科建设龙头地位凸显，学科门类布局不断完善和优化，现有理论经济学、应用经济学、工商管理学、统计学、公共管理学、马克思主义理论等6个一级学科硕士学位授权点；有工商管理（MBA）、金融（MF）、会计（MPAcc）、应用统计、税务、国际商务、资产评估、审计、法律、旅游管理（MTA）、公共管理（MPA）、电子信息等12个专业硕士学位授权点；有联合共建博士学位授权点1个。2023年，学校入选自治区“一流建设学科”建设高校，统计学一级学科入选自治区“一流建设学科”。近年来，以博士学位授权点建设为牵引，着力打造三大学科群、凝练十大特色研究方向、建设“6+1”知识创新与转化平台，持续增强服务社会能力，充分发挥学校在乡村振兴、中蒙俄经济走廊建设、政产企数字化转型等领域的人才保障和智力支撑作用，更好服务内蒙古五大任务建设。\n"
            "学校择优选择和重点建设了一批以经济、管理学科为主体的专业，构建了特色鲜明、优势明显的专业体系。开设53个本科招生专业，其中会计学、财政学、金融学3个国家级特色专业，金融学、国际经济与贸易、应用统计学、市场营销、会计学、旅游管理、财政学、法学、财务管理、物流管理、经济学、投资学、工商管理以及资产评估等14个专业入选国家级一流专业建设点，税收学、人力资源管理、贸易经济、会展经济与管理、计算机科学与技术、经济统计学、英语、审计学以及行政管理等9个专业入选自治区级一流本科专业建设点。现有4门国家级一流本科课程，28门自治区一流课程，3门自治区级课程思政示范课程。获批自治区优秀教学团队14个、课程思政教学团队3个，荣获国家优秀教学成果二等奖1项。获批3个自治区新文科研究与改革实践项目，其中，《“石榴籽工程”铸魂财经人才培养－新文科背景下培养模式重构》获教育部首批新文科研究与改革实践项目。\n"
            "学校现有普通高等教育在校生21336人。目前面向全国26个省、自治区、直辖市招生，享有较高的美誉度和影响力。学校将就业工作作为民生工程，形成全员参与就业、全年解决就业、全程指导就业的工作格局，就业率和就业质量居于自治区本科高校前列。学校被教育部评为“全国高校毕业生就业能力培训基地”“全国毕业生就业典型经验高校”“全国创新创业典型经验高校”，是自治区大学生创业培训基地，学校招生就业部门被评为自治区示范性就业指导中心。2024年校友会中国大学排名位居262位。建校以来，学校坚持以为党育人、为国育才为己任，牢记立德树人初心、坚守人才培养使命，累计培养各级各类人才18万余名，毕业生已经成为自治区乃至全国财政系统、审计系统、金融系统、税务系统、工商系统中的骨干与中坚力量，为自治区经济建设、社会发展、边疆稳定、民族团结做出了重要贡献。\n")
    info_window = tk.Toplevel(root)
    info_window.title("学校信息概况")
    info_window.geometry("800x600")

    text_widget = tk.Text(info_window, wrap=tk.WORD, font=("SimSun", 16))
    text_widget.insert(tk.END, info)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
    # messagebox.showinfo("学校信息概况", info)


def show_navigation_map():
    # 创建一个新窗口
    map_window = tk.Toplevel(root)
    map_window.title("导览地图")
    map_window.geometry("800x600")

    # 读取地理数据
    gdf = gpd.read_file('data.geojson')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号显示为方块的问题

    # 设置绘图区域
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # 绘制地理数据
    gdf.plot(ax=ax, edgecolor='k', facecolor='orange', alpha=0.5)
    ax.set_title('点击地图查看建筑物详情')

    # 设置横纵轴的标签格式为十进制
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.0f}'.format(val)))

    # 在Tkinter中显示matplotlib图像
    canvas = FigureCanvasTkAgg(fig, master=map_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    building_info_dict = {
        0: {'name': '内蒙古财经大学西校区', 'description': '学校始建于1960年，名称为内蒙古财经学院。1962年改建为内蒙古财贸干部进修学院，1965年改为内蒙古财贸学校。1979'
                                                 '年恢复本科招生，1980年经国务院批准复建内蒙古财经学院。2000'
                                                 '年学院与内蒙古经济管理干部学院合并成立新的内蒙古财经学院。2005年取得硕士学位授予权。2006'
                                                 '年内蒙古财税职业学院、内蒙古工商行政管理学校并入学院。2012'
                                                 '年经教育部批准，学院更名为内蒙古财经大学。学校是一所以本科和研究生教育为主、同时承担高等职业教育、继续教育培养任务，以经济学、管理学为主，理学、法学、文学、工学协调发展，具有鲜明财经特色的多科性应用研究型财经大学。作为我国民族地区高等财经教育的开创者、实践者和探索者，学校始终坚持为党育人、为国育才，坚持扎根边疆、服务西部，大力培养忠诚党的事业、具备国际视野、富有家国情怀、投身财经实践的杰出人才，为自治区乃至全国培养了大量各级各类人才，他们已经成为自治区财政、审计、金融、税务、工商企业等系统中的骨干与中坚力量，积极服务自治区“两个屏障”“两个基地”和“一个桥头堡”建设，为社会发展、边疆稳定、民族团结做出了重要贡献。',
            'photo': 'photo/内蒙古财经大学.jpg'},
        1: {'name': '西体育场', 'description': '内蒙古财经大学西体育场', 'photo': 'photo/西体育场.jpg'},
        2: {'name': '东体育场', 'description': '内蒙古财经大学东体育场', 'photo': 'photo/东体育场.jpg'},
        3: {'name': '图书馆', 'description': '内蒙古财经大学图书馆始建于1960年，西区图书馆为27000多平方米。', 'photo': 'photo/图书馆.jpg'},
        4: {'name': '体育馆', 'description': '内蒙古财经大学体育馆为现代化体育室内场馆，包括网球，篮球，羽毛球，乒乓球场地。', 'photo': 'photo/体育馆.jpg'},
        5: {'name': '学生公寓区', 'description': '内蒙古财经大学学生公寓', 'photo': 'photo/公寓区.jpg'},
        6: {'name': '第一餐厅', 'description': '内蒙古财经大学第一餐厅', 'photo': 'photo/第一食堂.jpg'},
        7: {'name': '第二餐厅', 'description': '内蒙古财经大学第二餐厅', 'photo': 'photo/第二食堂.jpg'},
        8: {'name': '学院楼', 'description': '学院楼是同学们上课的主要场所', 'photo': 'photo/学院楼.jpg'},
        9: {'name': '综合楼', 'description': '内蒙古财经大学综合楼', 'photo': 'photo/综合楼.jpg'},
    }

    def on_click(event):
        if isinstance(event, MouseEvent):
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                clicked_geom = gdf[gdf.geometry.apply(lambda geom: geom.contains(Point(x, y)))]
                if not clicked_geom.empty:
                    building_info_id = clicked_geom.index[-1]
                    building_info = building_info_dict.get(building_info_id)
                    if building_info:
                        show_building_info(building_info)

    def show_building_info(building_info):
        info_window = tk.Toplevel(root)
        info_window.title(building_info.get('name'))

        info_label = tk.Label(info_window, text=building_info.get('description'), wraplength=400)
        info_label.pack()

        photo_path = building_info.get('photo')
        if photo_path:
            image = Image.open(photo_path)
            image = image.resize((800, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            photo_label = tk.Label(info_window, image=photo)
            photo_label.image = photo  # 保持引用，防止图片被垃圾回收
            photo_label.pack()

    fig.canvas.mpl_connect('button_press_event', on_click)


# 添加菜单项
file_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="文件获取", menu=file_menu)
file_menu.add_command(label="解析地理要素", command=parse_geographic_data)
file_menu.add_command(label="打开 Shapefile", command=open_shapefile)

info_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="信息阅览", menu=info_menu)
info_menu.add_command(label="学校信息概况", command=show_school_info)

map_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="学校地图", menu=map_menu)
map_menu.add_command(label="导览地图", command=show_navigation_map)


# 创建按钮
def exit_program():
    root.quit()


#

exit_button = tk.Button(root, text="退出", command=exit_program)
exit_button.pack(side=tk.BOTTOM, pady=10)

photo_button = tk.Button(root, text="显示照片", command=show_images)
photo_button.pack(side=tk.BOTTOM, pady=20)

# 运行主循环
root.mainloop()
