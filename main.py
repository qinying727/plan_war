# coding:utf-8
#从Python3 开始，可以不写上面那句话了，python3是默认是uft8，可以处理程序中出现的中文。

'''
* @par          Copyright (C): 2023- , QinYing
* @file         main.py
* @author       QinYing
* @version      V1.0；Python 3.7.3；pygame 2.1.2
* @date         2022.02.8 ~ 2022.02.27 已打包成exe文件。
* @brief        根据编程侯老师教学飞机大战游戏的教学视频编写，用于辅导靖涵。
* @details
* @par History
* @版本			V1.0
'''

#安装打包成exe工具命令：pip install auto-py-to-exe -i https://pypi.tuna.tsinghua.edu.cn/simple

import pygame # 使用该命令安装：pip install pygame -i https://pypi.tuna.tsinghua.edu.cn/simple
import random
import os
import pathlib

FPS = 60 #游戏界面每秒刷新次数
WIDTH = 500 #游戏界面的宽
HEIGHT = 500 #游戏界面的高
WHITE = (255,255,255) #游戏界面背景色的RGB值
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK = (0,0,0)

#游戏初始化
pygame.init()
pygame.mixer.init() #初始化声音混合器，以便引入背景音乐。
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('飞机大战')
clock = pygame.time.Clock() # 创建时钟对象（控制游戏的FPS）

#获取当前文件夹所在的绝对路径，打包的时候把程序中原来使用的相对路径改成绝对路径，这样在别的电脑上运行不会出错。把folder放入所有os.path.join的第一个参数
folder = pathlib.Path(__file__).parent.resolve()

# 设置背景图片和角色的图片
# 使用 convert 可以转换格式，提高程序绘制图片（blit 或者 draw）的执行效果。
background_img = pygame.image.load(os.path.join(folder, "img", "background.png")).convert()
player_img = pygame.image.load(os.path.join(folder, "img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(25, 20)) # 把战机图片尺寸缩小到指定尺寸，用来表示战机的生命数量
player_mini_img.set_colorkey(BLACK) # 设置透明度

#设置游戏界面左上角的图标
pygame.display.set_icon(player_mini_img)

rock_img = pygame.image.load(os.path.join(folder, "img", "rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join(folder, "img", f"rock{i}.png")).convert())
bullet_img = pygame.image.load(os.path.join(folder, "img", "bullet.png")).convert()

expl_anim = {} #定义空字典，用于存储爆炸效果的图片
expl_anim['lg'] = [] #定义字典里的一个元素‘lg’（large）为一个空列表,存放大陨石爆炸图片；
expl_anim['sm'] = [] #定义字典里的一个元素‘sm’（small）为一个空列表,存放小陨石爆炸图片；
expl_anim['player'] = [] # 存放战机爆炸图片
# 把爆炸的9张图片依次加载进来，放入lg和sm两个列表中
for i in range(9):
    expl_img = pygame.image.load(os.path.join(folder,"img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK) # 设置背景颜色
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75,75))) # 大的图片放入列表lg中，大小为75*75
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30,30))) # 小的图片放入列表lg中，大小为30*30
    player_expl_img = pygame.image.load(os.path.join(folder,"img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)

#宝箱掉落的图片引入
power_imgs = {} #定义空字典，用于存储宝箱的图片
power_imgs['shield'] = pygame.image.load(os.path.join(folder,"img","shield.png")).convert() #定义字典里的一个元素‘shield’列表,存放盾牌宝箱图片，吃了之后可以加血；
power_imgs['gun'] = pygame.image.load(os.path.join(folder,"img","gun.png")).convert() #定义字典里的一个元素‘gun’列表,存放子弹宝箱图片，吃了之后可以双发子弹；

# 设置射击音乐
shoot_sound = pygame.mixer.Sound(os.path.join(folder,"sound","shoot.wav")) #射击声音

# 设置击中陨石爆炸声音sound文件夹中有两种爆炸声音，放入列表中，随机选择爆炸声音
expl_sounds = [
    pygame.mixer.Sound(os.path.join(folder,"sound","expl0.wav")),#第一种爆炸声音
    pygame.mixer.Sound(os.path.join(folder,"sound","expl1.wav")) #第二种爆炸声音
]

# 设置战机爆炸音乐
die_sound = pygame.mixer.Sound(os.path.join(folder,"sound","rumble.ogg"))

# 设置宝箱音乐
shield_sound = pygame.mixer.Sound(os.path.join(folder,"sound","pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join(folder,"sound","pow1.wav"))

#设置背景音乐,和前面两种声音的代码有区别
pygame.mixer.music.load(os.path.join(folder,"sound","background.ogg"))
pygame.mixer.music.set_volume(0.3)#设置背景音乐音量

# 引入字体，显示战机得分
#font_name = pygame.font.match_font('arial') # 注意这个字体不能显示中文，所以开机画面的文字无法显示
font_name = os.path.join(folder,'font.ttf')

'''
* @function     draw_text
* @author       QinYing
* @date         2023.02.19
* @brief        绘制战机得分。
* @var          surf：绘制的位置；text:绘制的内容；size:文字大小; xy:位置坐标
* @par History
'''
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size) #调用pygame中的字体类来定义一个字体对象（克隆体）
    text_surface = font.render(text, True, WHITE) # 渲染字体；True是字体是否反锯齿，显示效果好一些。
    text_rect = text_surface.get_rect()#获得文字的外框
    text_rect.centerx = x
    text_rect.top = y #注意这里用的是top，而不是centery，没有深究原因
    surf.blit(text_surface, text_rect)

'''
* @function     draw_health
* @author       QinYing
* @date         2023.02.22
* @brief        绘制战机血量。
* @var          surf：绘制的位置；hp:血量值；xy:位置坐标
* @par History
'''
def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0 #避免血量出现负值
    BAR_LENGTH = 100 # 血量条的长度
    BAR_HEIGHT = 10  # 血量条的高度
    fill = (hp/100)*BAR_LENGTH # hp/100是剩余血量的百分比，因此fill代表实际填充的长度
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) #调用pygame生成一个Rect类的对象（克隆体），作为血量条的外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT) # 血量的长方形
    pygame.draw.rect(surf, GREEN, fill_rect) # 把长方形绘制出来
    pygame.draw.rect(surf, WHITE, outline_rect, 2) #最有一个参数2表示只显示宽度为2的边框，不用白色填充内部，避免外框把内框覆盖，看不到血量的变化。

'''
* @function     draw_lives
* @author       QinYing
* @date         2023.02.22
* @brief        绘制战机有几条命。
* @var          surf：绘制的位置；lives:生命梳理；xy:位置坐标
* @par History
'''
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img,img_rect)

'''
* @function     new_rock
* @author       QinYing
* @date         2023.02.22
* @brief        陨石和子弹/战机撞击并消失后，重新生成陨石，避免陨石越来越少。
* @var          none
* @par History
'''
def new_rock():
    rock = Rock()  # 石头消失后再生成一个，防止石头越来越少。
    all_sprites.add(rock)
    rocks.add(rock)

'''
* @function     draw_init
* @author       QinYing
* @date         2023.02.26
* @brief        绘制开机画面。
* @var          none
* @par History
'''
def draw_init():
    screen.blit(background_img, (0, 0))  # 在原点（0,0）的位置放置背景图片。
    draw_text(screen, "飞机大战", 62, WIDTH / 2, HEIGHT / 4) #后面三个参数分别是大小以及XY坐标
    draw_text(screen, "左右键移动战机，空格键发射子弹", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "任意键开始", 18, WIDTH / 2, WIDTH * 3 / 4)
    pygame.display.update()
    waiting = True # 等待按键按下才进入游戏
    while waiting:
        clock.tick(FPS)  # 通过时钟对象，指定While循环的频率，每秒循环FPS次。也就是游戏界面每秒更新60次。
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True #第10个视频6分20秒左右讲的，表示以及初始化结束了,会传到主程序close变量里。没有这一句以及后面不设置close变量代码也能正确运行，但打包成exe文件后可能出问题。原理不是太清楚。
            elif event.type == pygame.KEYUP:  # 侦测有按键被按下并放开，也就是抬起某个按键
                waiting = False
                return False

'''
* @class        Player
* @author       QinYing
* @date         2023.02.09
* @brief        定义一个战机的类。相当于Scratch中的角色
* @functions    __init__(self): 用pygame定义该类 以及 战机的一些初始属性
* @functions    update(self): 更新战机的状态（各类属性）		
* @par History
'''
class Player(pygame.sprite.Sprite): # 这个类（角色）是Pygame中的Sprite类型，可以使用Sprite的各种方法（函数）
    def __init__(self): # 定义初始化自己的方法,定义角色的一些属性
        pygame.sprite.Sprite.__init__(self) # 这个类定义的前三行是固定写法。是用Sprite来初始化自己（self）。
        #self.image = pygame.Surface((50,40)) #定义战机的大小
        #self.image.fill(GREEN)  # 定义战机的颜色
        self.image = pygame.transform.scale(player_img,(50,40)) #把图片调整到指定的大小
        self.image.set_colorkey(BLACK) #把战机图片的背景设置为透明。

        #定义战机的初始位置
        self.rect = self.image.get_rect()#获取能包住战机的长方形。参考编程侯老师视频：从零开始用Python制作飞机大战第2集【角色移动】
        self.radius = 25  # 定义一个圆的半径大小，用圆形框定飞机的轮廓，相比较长方形而言，提升和陨石碰撞的精确性
        # 把圆画到战机图片上以便能看到效果，红色，圆心在战机的中心，半径为self.radius。画圆的代码必须在摆放战机的代码之前，否则看不到画的圆。
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        #self.rect.center = (WIDTH/2,HEIGHT/2) #设置战机在游戏窗口中的起始位置在游戏界面中央.
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 20 #Python中以画面左上角作为坐标系的原点（0,0），X和Y左边分别向右、向下延展为正数方向。

        self.speedx = 8 #对象（克隆体）横向移动的速度是8。注意这里给类添加属性的写法。应该是这个类的私有变量。
        self.health = 100 #初始生命值（血量）为100
        self.lives = 3
        self.hidden = False #设定战机是否隐藏
        self.gun = 1 # 战机默认是发射一个子弹

    def update(self):
        now = pygame.time.get_ticks()
        key_press = pygame.key.get_pressed() #返回键盘所有的按键情况，在get_pressed这个列表中把对应的按键赋值true 或者 false
        # 使用键盘的左右键控制飞机移动
        if key_press[pygame.K_RIGHT]:
            self.rect.x += self.speedx #self.rect.x = self.rect.x + self.speedx 的简略写法。让物体动起来。

        if key_press[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        #处理飞机碰到游戏界面的边缘的情况
        #if self.rect.x > WIDTH: #如果碰到右边了
        #    self.rect.x = 0 # 回到最左边

        if self.rect.right > WIDTH: #如果碰到右边了
            self.rect.right = WIDTH # 固定在最右边

        if self.rect.left < 0:
            self.rect.left = 0

        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000: # 如果隐藏状态已经大于1000毫秒了
            self.hidden = False # 取消隐藏
            self.rect.centerx = WIDTH / 2 #把战机放到初始化的位置，就显示出来了
            self.rect.bottom = HEIGHT - 20

        if self.gun > 1 and now - self.gun_time > 5000: #判断战机获得子弹宝箱是否超过5秒
            self.gun = 1

    # 定义发射子弹的函数
    def shoot(self):
        if not (self.hidden): # 判断飞机是否是隐藏状态。飞机被打没有血量后会隐藏1秒钟
            if self.gun == 1: # 飞机可以发射一颗子弹
                bullet = Bullet(self.rect.centerx, self.rect.centery)  # 子弹发射的位置就是战机的位置
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2: # 飞机可以发射2颗子弹
                bullet1 = Bullet(self.rect.left, self.rect.centery)  # 子弹发射的位置是战机长方形的左边
                bullet2 = Bullet(self.rect.right, self.rect.centery) # 子弹发射的位置是战机长方形的右边
                all_sprites.add(bullet1)
                bullets.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
                shoot_sound.play()

    #
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks() # 得到当前时间
        self.rect.center = (WIDTH/2, HEIGHT+500) # 放到舞台外面，达到隐藏的目的

    # 吃了gun宝箱后，生成双排子弹
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()#记录获得宝箱的时间，用于控制宝箱效果的有效期

'''
* @class        Rock
* @author       QinYing
* @date         2023.02.10
* @brief        定义一个陨石的类。相当于Scratch中的角色
* @functions    __init__(self): 用pygame定义该类 以及 陨石的一些初始属性
* @functions    update(self): 更新陨石掉落的状态（各类属性）		
* @par History
'''
class Rock(pygame.sprite.Sprite):
    def __init__(self): # 定义初始化自己的方法,定义角色的一些属性
        pygame.sprite.Sprite.__init__(self) # 这个类定义的前三行是固定写法。self代表“自己”,并且是用pygame定义出来的一个“自己”，这样在下面才可以用self调用pygame中的一些方法（函数），比如self.rect.center等。
        #self.image = pygame.Surface((30,30)) #定义石块的大小
        #self.image.fill(RED) #
        #self.image = rock_img  # 图片大小合适，不用像战机那样调整大小
        #self.image_origin = rock_img # 陨石的原始图片，陨石每次旋转都以这个原始图片为基准旋转
        self.image_origin = random.choice(rock_imgs) # 从数组中随机选择一个陨石的图片。
        self.image_origin.set_colorkey(BLACK)  # 把图片的背景设置为透明。
        self.image = self.image_origin.copy() # 拷贝一份陨石图片。

        # 陨石的初始位置
        self.rect = self.image.get_rect()
        #self.radius = self.rect.width / 2  # 定义一个圆的半径大小，半径是陨石长方形宽度的一半
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # 把圆画到陨石图片上，红色，圆心在陨石的中心，半径为self.radius

        self.rect.x = random.randrange(0,WIDTH - self.rect.width) # 舞台宽度减去陨石本身的宽度
        self.rect.y = random.randrange(-180,-100)

        self.speedy = random.randrange(1,2) #对象（克隆体）纵向移动的速度。注意这里给类添加属性的写法。
        self.speedx = random.randrange(-3,3) #对象（克隆体）横向移动的速度，让陨石不是垂直掉落。

        self.rot_degree = random.randrange(-3, 3) #陨石每次旋转的角度
        self.total_degree = 0 #陨石一共旋转了多少度,初始值为0.

    #定义石头旋转效果的函数
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360 #取余操作，角度不能超过360度
        # 把image_origin旋转后赋值给image。
        '''
        pygame实现图像连续旋转的几个步骤：
        1）要有2个图片，一个是原始图片对象（origin），一个是副本对象(copy)。在初始化中完成。
        2）以原始图片为基准，进行图片旋转，把旋转后的图片赋值给copy对象。这时copy对象的角度是旋转过的，origin对象的图片未作改变。代码为：self.image = pygame.transform.rotate(self.image_origin, self.total_degree)
        3）获取到copy对象的中心位置center，由于copy对象的x、y轴在不断变化，这时copy对象和origin对象的位置可能已经离的很远了：代码为：self.rect.center = center
        4）基于这个中心位置绘制屏幕，显示的是copy对象，origin对象始终不改变，用来生成旋转后的图像。代码为：all_sprites.draw(screen) 以及 pygame.display.update()
        5）以上步骤每秒进行FPS次，本程序中为每秒60次。
        6）相关原理参考：第7集7分30秒处的讲解，重点参考：https://blog.csdn.net/qq_55851641/article/details/118529993
        '''
        self.image = pygame.transform.rotate(self.image_origin, self.total_degree) #pygame.transform.rotate(surface,angle)返回一个旋转后的surface对象，默认是按照逆时针进行旋转的，当angle小于0时则代表的顺时针进行旋转
        center = self.rect.center #取到陨石副本（copy）未转动时长方形外框的中心点
        self.rect = self.image.get_rect() #重新获取旋转后陨石副本（copy）图片的外框
        self.rect.center = center #把旋转后陨石外框的中心点拉回到原来长方形的中心点。

    def update(self): # 陨石不断掉落的函数
        self.rotate() # 由于刷新率FPS设置为60，每次旋转角度为（-3，3）的随机数，所以一个石块一秒钟最多最多旋转3*FPS = 180度。
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # 陨石超过游戏界面的边界（底部、左边、右边）后重新从上面向下掉
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)  # 舞台宽度减去陨石本身的宽度
            self.rect.y = random.randrange(-100, -40)

            self.speedy = random.randrange(1, 2)  # 对象（克隆体）纵向移动的速度。注意这里给类添加属性的写法。
            self.speedx = random.randrange(-3, 3)  # 对象（克隆体）横向移动的速度，让陨石不是垂直掉落。

'''
* @class        Bullet
* @author       QinYing
* @date         2023.02.10
* @brief        定义战机子弹的类。相当于Scratch中的角色
* @functions    __init__(self): 用pygame定义该类 以及 子弹的一些初始属性
* @functions    update(self): 		
* @par History
'''
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y): # 定义初始化自己的方法,定义角色的一些属性。新增了x,y两个参数，用于传入战机的位置参数，以便将子弹的位置和战机的位置保持一致。
        pygame.sprite.Sprite.__init__(self) # 这个类定义的前三行是固定写法。self代表“自己”,并且是用pygame定义出来的一个“自己”，这样在下面才可以用self调用pygame中的一些方法（函数），比如self.rect.center等。
        #self.image = pygame.Surface((10,20)) #定义子弹的大小
        #self.image.fill(YELLOW) #定义子弹的颜色
        self.image = bullet_img
        self.image.set_colorkey(BLACK)  # 把图片的背景设置为透明。

        # 子弹的初始位置
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speedy = -10

    def update(self): # 子弹不断变化位置的函数
        self.rect.y += self.speedy

        # 子弹超过游戏界面的顶部后消失
        if self.rect.bottom < 0:
            self.kill() # 相当于Scratch里的删除克隆体。

'''
* @class        Explosion
* @author       QinYing
* @date         2023.02.25
* @brief        定义爆炸的类。相当于Scratch中的角色
* @functions    __init__(self): 用pygame定义该类 以及 陨石的一些初始属性
* @functions    update(self): 		
* @par History
'''
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size): # 定义初始化自己的方法,定义角色的一些属性。center参数用于传入爆炸对象重点点的位置,size是爆炸的大小
        pygame.sprite.Sprite.__init__(self) # 这个类定义的前三行是固定写法。self代表“自己”,并且是用pygame定义出来的一个“自己”，这样在下面才可以用self调用pygame中的一些方法（函数），比如self.rect.center等。
        self.size = size
        self.image = expl_anim[self.size][0] #引用字典里数组内元素的方法
        # self.image.set_colorkey(BLACK)  # 图片放入字典内数组的时候已经处理过透明度了，这里就不用再处理了。

        # 设置爆炸图形的位置
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 #每个爆炸效果是由很多张图片组成的，这里定义一个帧数的变量，0表示从数组的第0张开始
        self.last_update = pygame.time.get_ticks() #记录初始化的时间

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50: #当前时间减去初始化的时间大于设定时间间隔（毫秒），切换图片
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]): # 如果爆炸效果列表中最后一张图片都用过了，删除对象
                self.kill()
            else: # 列表中有图片还没有用过，则显示下一张图片
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

'''
* @class        Power
* @author       QinYing
* @date         2023.02.26
* @brief        定义宝箱的类。相当于Scratch中的角色
* @functions    __init__(self): 用pygame定义该类 以及 宝箱的一些初始属性
* @functions    update(self): 		
* @par History
'''
class Power(pygame.sprite.Sprite):
    def __init__(self,center): # 定义初始化自己的方法,定义角色的一些属性。center参数用于传入宝箱的位置中心位置。
        pygame.sprite.Sprite.__init__(self) # 这个类定义的前三行是固定写法。self代表“自己”,并且是用pygame定义出来的一个“自己”，这样在下面才可以用self调用pygame中的一些方法（函数），比如self.rect.center等。
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)  # 把图片的背景设置为透明。

        #宝箱音乐
        if self.type == 'shield':
            shield_sound.play()
        elif self.type == 'gun':
            gun_sound.play()

        # 宝箱的初始位置
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.speedy = 3

    def update(self): # 宝箱不断变化位置的函数
        self.rect.y += self.speedy

        # 宝箱超过游戏界面的底部后消失
        if self.rect.top > HEIGHT:
            self.kill() # 相当于Scratch里的删除克隆体。

'''
#被注释的这一整段代码都放入主函数里了
all_sprites = pygame.sprite.Group()# 调用pygame方法生成一个列表，用来存储这个游戏中所有的对象（也就是克隆体），包括战斗机和障碍物
rocks = pygame.sprite.Group() #用于存放陨石对象的列表
bullets = pygame.sprite.Group() #用于存放子弹对象的列表
powers = pygame.sprite.Group() #用于存放宝箱对象的列表
player = Player() #生成一个Player类的对象player; 相当于Scratch里生成一个角色的克隆体。
all_sprites.add(player)
score = 0 # 战机的得分
pygame.mixer.music.play(-1) #无限次重复播放背景音乐

for i in range(8): #生成8个陨石
    new_rock()
'''

show_init = True #是否显示开场画面
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break #停止重复执行
        show_init = False #显示过开场画面后把show_init改为False
        all_sprites = pygame.sprite.Group()  # 调用pygame方法生成一个列表，用来存储这个游戏中所有的对象（也就是克隆体），包括战斗机和障碍物
        rocks = pygame.sprite.Group()  # 用于存放陨石对象的列表
        bullets = pygame.sprite.Group()  # 用于存放子弹对象的列表
        powers = pygame.sprite.Group()  # 用于存放宝箱对象的列表
        player = Player()  # 生成一个Player类的对象player; 相当于Scratch里生成一个角色的克隆体。
        all_sprites.add(player)
        score = 0  # 战机的得分
        pygame.mixer.music.play(-1)  # 无限次重复播放背景音乐

        for i in range(8):  # 生成8个陨石
            new_rock()
    clock.tick(FPS) # 通过时钟对象，指定While循环的频率，每秒循环FPS次。也就是游戏界面每秒更新60次。
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN: #侦测有按键被按下
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 刷新列表中所有对象（相当于Scratch中的克隆体）状态
    # pygame库中的update函数对各个类中同名的函数的影响参考：https://www.jianshu.com/p/126ef3e4e36e。
    # 简单来说就是在pygame.sprite.Group()中有update()方法，在各个类中也定义一个同样名称的update方法，在可以通过下面的语句一次性调用所有对象的update方法。
    # 根据上面的FPS值，所有对象（克隆体）每秒update60次。
    all_sprites.update()

    # 子弹与陨石的碰撞检测，必须在all_sprites.update()之后执行。使用pygame自带的函数groupcollide进行碰撞检测。
    # 后面两个True代表检测的碰撞就把列表中对应的对象删除
    # 函数返回值是发生碰撞的rocks,记录在hits_rockandbullet列表中。
    hits_rockandbullet = pygame.sprite.groupcollide(rocks, bullets, True, True)

    # 当陨石被打中消失后，再生成一个陨石。否则游戏中很快就没有陨石了。并随机生成宝箱
    for hit in hits_rockandbullet:
        random.choice(expl_sounds).play() #子弹打到陨石的时候从爆炸声音列表中随机选择一个爆炸的声音播放
        expl = Explosion(hit.rect.center,'lg') # 石头被子弹击中会爆炸
        all_sprites.add(expl)
        new_rock()

        #击中陨石后得分
        score = score + int(hit.radius)

        # 随机生成宝箱
        if random.random() > 0.1: #随机生成一个0~1的数字，如果大于0.1（也就是90%的概率）就生成一个宝箱
            p = Power(hit.rect.center) # 在撞击位置的正中间生成一个宝箱
            all_sprites.add(p)
            powers.add(p) # 宝箱可能有多个，所以宝箱也放到一个独立的列表中处理

    #处理战机与宝箱相撞
    hits_playerandpower = pygame.sprite.spritecollide(player, powers, True)  # 这里用第三个参数用False不删除宝箱powers，用True则删除powers。
    for hit in hits_playerandpower:  # 复制过来的注释不改了————第8集视频又说hits_rockandbullet是一个字典，与子弹撞击陨石的写法很像
        if hit.type == 'shield':
            player.health += 20 #玩家血量增加20
            if player.health >= 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()

    # 飞机（一个角色）和陨石（很多角色）的碰撞检测,用Pygame自带的spritecollide实现。如果碰撞了，返回值是true
    hits_playerandrock = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle) # 这里用第三个参数用False，不删除战机和石头。用True则删除，从效果看，好像只删除了陨石。
    # 如果要直接结束游戏，用下面2行代码
    # if hits_rockandbullet: # 感觉这里有个隐患，飞机撞陨石和子弹撞陨石两个函数返回值都给了一个相同名称的变量hits_rockandbullet，感觉应该用不同名称的变量会好一点。在第8集6分钟的时候，把名称改成了hits_playerandrock
    #     running = False

    #如果要战机没有血量后再结束游戏，用下面代码
    for hit in hits_playerandrock: #第8集视频又说hits_rockandbullet是一个字典，与子弹撞击陨石的写法很像
        player.health -= hit.radius
        new_rock() # 生成新的石头，否则石头就没有了
        expl = Explosion(hit.rect.center, 'sm') # 石头碰到战机会爆炸
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')  # 战机爆炸
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide() # 旧的战机没有血量后，战机先隐藏一下，1000毫秒后再显示，这样看起来就像是新出来了一个战机
        if player.lives == 0:
            #running = False
            show_init = True #进入开始界面，而非直接退出游戏

    #显示画面
    screen.fill(BLACK) #设定游戏屏幕颜色，默认是黑色。
    screen.blit(background_img,(0,0)) #在原点（0,0）的位置放置背景图片。
    all_sprites.draw(screen) # 调用Pygame的draw函数依次将数组中的元素绘制在screen上
    draw_text(screen, str(score), 18, WIDTH/2, 0)
    draw_health(screen, player.health, 10, 30)
    draw_lives(screen, player.lives, player_mini_img, WIDTH-100, 15)
    pygame.display.update()  #对显示窗口进行更新，默认窗口全部重绘
pygame.quit()