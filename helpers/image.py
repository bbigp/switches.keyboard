import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from datetime import datetime
from threading import Timer
import io
import json
from tkinter.scrolledtext import ScrolledText

import requests
from PIL import ImageGrab, ImageTk

print(f'TkVersion: {tk.TkVersion}')

# https://blog.csdn.net/geng_zhaoying/article/details/119096475
def screen_grab():
    global f1,cv,TRANSCOLOUR        #在Toplevel窗口和主窗口可以互相使用对方的变量和方法。
    root.state('icon')              #主窗体最小化。icon:最小化,normal:正常显示,zoomed:最大化。或root.iconify()
    f1 = tk.Toplevel(root)                   #用Toplevel类创建独立主窗口的新窗口，非模式窗体
    f1.wm_attributes("-alpha", 0.7)          #设置窗体透明度(0.0~1.0)
    f1.overrideredirect(True)                #设置窗体无标题栏
    ws = f1.winfo_screenwidth()              #屏幕长和宽
    hs = f1.winfo_screenheight()
    s=str(ws)+'x'+str(hs)+'+0+0'
    f1.geometry(s)                  #Toplevel窗体充满屏幕,整个屏幕似乎被雾遮住,点击屏幕任意处,将使该窗体退出
    TRANSCOLOUR = 'gray'
    f1.wm_attributes('-transparentcolor', TRANSCOLOUR)  #设置灰色为透明颜色
    cv = tk.Canvas(f1)                                  #在Toplevel窗体增加Canvas实例，用来画透明矩形
    cv.pack(fill=tk.BOTH, expand=tk.Y)                  #使Canvas实例自动充满Toplevel窗体
    tk.Button(cv,text="关闭", command=close_dialog).pack(side='right')     #该按钮将出现在屏幕右侧中间位置
    cv.bind("<ButtonPress-1>", start_move)  #绑定鼠标左键按下事件，为在Toplevel窗体上拖动鼠标画矩形做准备
    cv.bind("<ButtonRelease-1>",stop_move) #绑定鼠标左键松开事件
    cv.bind("<B1-Motion>", on_motion)      #绑定鼠标左键被按下时移动鼠标事件
def close_dialog():
    f1.destroy()            #关闭对话框
    root.state('normal')    #使主窗体正常显示
def start_move(event):       #为拖动画矩形做准备
    global first_x,first_y,cv
    first_x,first_y = event.x,event.y       #拖动鼠标画矩形其左上角坐标必须记住，保持不变
    cv.create_rectangle(first_x,first_y,event.x+1,event.y+1,fill=TRANSCOLOUR, outline=TRANSCOLOUR,tags=('L'))
def stop_move(event):                #鼠标抬起，截取所选择屏幕区域图像
    global first_x,first_y,cv,f1,img,p
    if abs(first_x-event.x)<10 or abs(first_y-event.y)<10:      #如截取的图像太小无意义，可能是误操作
        cv.delete('L')                                          #删除这个误操作所画矩形
        return
    x=f1.winfo_rootx()+first_x      #x=Toplevel窗体在屏幕坐标系中的x坐标+所画透明矩形左上角x坐标
    y=f1.winfo_rooty()+first_y
    x1=x+abs(first_x-event.x)       #abs(first_x-event.x)是所画透明矩形的宽
    y1=y+abs(first_y-event.y)       #abs(first_y-event.y)是所画透明矩形的高
    p=ImageGrab.grab((x,y,x1,y1))   #截取屏幕透明矩形内图像。因PIL的问题，必须将显示设置里的缩放比例调成100%
    new_width, new_height = calculate_resize_dimensions(x1-x, y1-y, 400, 300)
    img = ImageTk.PhotoImage(image=p.resize((new_width, new_height)))              #将image1转换为canvas能显示的格式
    cvM.delete('P')                                #删除上一个截取图像
    cvM.create_image(0,0,image=img,tags=('P'),anchor=('nw'))   #将img在主窗口显示,img必须是全局变量,不能丢失
    f1.destroy()                    #关闭Toplevel窗体
    root.state('normal')            #使主窗体正常显示
    upload()
def on_motion(event):                #拖动画矩形
    global first_x,first_y,cv
    cv.coords('L',first_x,first_y,event.x,event.y)  #移动透明矩形到新位置,左上角坐标不变,右下角为新位置
def grab_all_screen():                    #截全屏
    root.state('icon')                  #如在该函数内直接截屏，主窗体动画最小化未完成，主窗体将被截到。
    t = Timer(0.2, do_grab_all_screen)     #后来创建事件,在此发出事件,在事件函数中截屏,问题未解决。
    #最后用多线程,上句创建定时器,0.2秒后在其它线程执行参数2指定函数。由于时间延迟,显得截图略慢
    t.start()       #此句启动定时器。如主窗体仍被截到，可将0.2秒变大，例如0.3、0.4、0.5等。
def save_image():                        #保存截屏所得图像。下句打开对话框,选择保存文件夹及文件名和扩展名
    fname=tkinter.filedialog.asksaveasfilename(title=u'保存文件')
    p.save(str(fname))
def help(): #帮助按钮事件处理函数
    s='因PIL的问题,显示设置的缩放比例必须调成100%,否则截图尺寸出错。\n'+\
    '单击"定位截屏"按钮,整个屏幕似被雾遮住，鼠标点击要截屏图像左上角后,\n'+\
    '拖动鼠标画矩形,矩形内雾被去掉,抬起鼠标,截图显示到主窗体,雾全部消失'+\
    '\n保存文件必须填写文件名和图像扩展名。截全屏后显示图像为原图的0.87,'+\
    '\n但保存的文件尺寸未改变。                              保留所有版权'
    tkinter.messagebox.showinfo(title="帮助",message=s)
def do_grab_all_screen():  #Timer(0.2,doGrabAllScreen)语句参数2指定的在其它线程执行的方法。实际的截全屏方法
    global img,p
    ws = root.winfo_screenwidth()              #屏幕长和宽
    hs = root.winfo_screenheight()
    p=ImageGrab.grab((0,0,ws,hs))#截全屏。因PIL的问题,必须将显示设置里的缩放比例调成100%,否则截取尺寸出错
    new_width, new_height = calculate_resize_dimensions(ws, hs, 400, 300)

    img = ImageTk.PhotoImage(image=p.resize((new_height, new_height)))              #将image1转换为canvas能显示的格式
    cvM.delete('P')                                 #删除上一个截取图像
    cvM.create_image(0,0,image=img,tags=('P'),anchor=('nw'))#将img在主窗口显示,img必须是全局变量,不能丢失
    root.state('normal')                           #使主窗体正常显示

def upload():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    host = entry.get()
    buff = io.BytesIO()
    p.save(buff, format='PNG')
    files = {'image': buff.getvalue()}
    response = requests.post(f'{host}/api/upload_temp_pic', files=files)
    if response.status_code == 200:
        data = json.loads(response.text)
        print(f'{now} {data}')
        if data['status'] == 'ok':
            text.insert('1.0', f"{now} 上传成功: {data['data'].replace('/bfs/fs/', '')}\n")
            # cvM.delete('P')
        else:
            text.insert('1.0', f"{now} 上传失败\n")
    else:
        text.insert('1.0', f"{now} 请求失败: {response.status_code}\n")

def calculate_resize_dimensions(image_width, image_height, display_width, display_height):
    # 计算图片的宽高比和显示空间的宽高比
    image_ratio = image_width / image_height
    display_ratio = display_width / display_height

    if image_ratio > display_ratio:
        # 图片的宽高比大于显示空间的宽高比，将图片宽度设置为显示空间的宽度，高度按比例缩小
        new_width = display_width
        new_height = int(new_width / image_ratio)
    elif image_ratio < display_ratio:
        # 图片的宽高比小于显示空间的宽高比，将图片高度设置为显示空间的高度，宽度按比例缩小
        new_height = display_height
        new_width = int(new_height * image_ratio)
    else:
        # 图片的宽高比等于显示空间的宽高比，无需调整
        new_width = display_width
        new_height = display_height

    return new_width, new_height


root = tk.Tk()
root.wm_title('Bigp')
root.geometry('400x400-50-50')
frm = tk.Frame(root)
frm.pack(fill=tk.BOTH)
entry = tk.Entry(frm, width=200)
entry.insert(index=0, string='http://onlybox.cn:8002')
entry.pack()
tk.Button(frm, text="定位截屏", command=screen_grab).pack(side='left')
tk.Button(frm, text="截全屏", command=grab_all_screen).pack(side='left')
tk.Button(frm, text="保存图像", command=save_image).pack(side='left')
tk.Button(frm, text="上传", command=upload).pack(side='left')
cvM = tk.Canvas(root, bg='lightgray', height=280, width=400)        #主窗体中canvac实例
cvM.pack()
text = ScrolledText(root)
text.pack()

if __name__ == '__main__':
    root.mainloop()