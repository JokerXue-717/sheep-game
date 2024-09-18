import pygame
from pygame.locals import *
from sys import exit
from random import randint, shuffle

redColor = pygame.Color(255, 0, 0)  # 用于显示时间用完
# 初始化pygame.mixer模块以支持MP3格式
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

windows_width = 400
windows_height = 760
icoSize = 48
whiteColor = pygame.Color(255, 255, 255)
blackColor = pygame.Color(0, 0, 0)
blueColor = pygame.Color(0, 0, 255)  # 用于高亮显示

# 加载图案图片并调整大小
sheepImages = []
for i in range(1, 10):
    try:
        image = pygame.image.load(f'images/tile{i}.png')
        sheepImages.append(pygame.transform.scale(image, (icoSize, icoSize)))
    except pygame.error as e:
        print(f"无法加载图片: {e}")

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

def draw_victory_screen(playSurface, largeFont, font):
    playSurface.fill(whiteColor)
    text = largeFont.render("You Win!", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 3))
    text = font.render("Press 'R' to Restart or 'Q' to Quit", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 2))

def draw_intro_screen(playSurface, largeFont, font):
    playSurface.fill(whiteColor)
    text = largeFont.render("Welcome to Sheep Game!", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 3))
    text = font.render("Press 'E' for Easy Mode", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 2))
    text = font.render("Press 'H' for Hard Mode", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, 2 * windows_height // 3))

def draw_game_over_screen(playSurface, largeFont, font, totalScore):
    playSurface.fill(whiteColor)
    text = largeFont.render("Game Over!", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 3))
    text = font.render("Score: " + str(totalScore), True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, windows_height // 2))
    text = font.render("Press 'R' to Restart or 'Q' to Quit", True, blackColor)
    playSurface.blit(text, (windows_width // 2 - text.get_width() // 2, 2 * windows_height // 3))

def draw_border(playSurface, color, width):
    rectangle = pygame.Rect(0, 0, windows_width, windows_height)
    pygame.draw.rect(playSurface, color, rectangle, width)

def provide_feedback():
    # 提供声音反馈
    try:
        click_sound = pygame.mixer.Sound('click.mp3')
        click_sound.play()
    except pygame.error as e:
        print(f"无法播放音效: {e}")

def main():
    global totalScore, score, itemCount, store, data, gameOver, intro, difficulty, winCount, startTime, countdown
    totalScore = 0
    score = 0
    itemCount = 5
    winCount = 0  # 胜利计数器
    countdown = 300  # 倒计时时间，单位秒，改为300秒
    pygame.init()
    fpsClock = pygame.time.Clock()
    playSurface = pygame.display.set_mode((windows_width, windows_height))
    pygame.display.set_caption("猫了个猫")
    defaultFont = pygame.font.get_default_font()
    font = pygame.font.SysFont(defaultFont, 24)
    largeFont = pygame.font.SysFont(defaultFont, 36)
    intro = True
    gameOver = False
    difficulty = 'easy'  # Default difficulty
    startTime = None  # 用于存储游戏开始的时间

    offsetX = (windows_width - (2 * (icoSize + 48) + 48)) // 2
    offsetY = (windows_height - (2 * (icoSize + 48) + 48)) // 2

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN:
                if intro:
                    if event.key == K_e:
                        difficulty = 'easy'
                        targetCount = 15 * 3  # 每种图片15次，共3种
                        intro = False
                        provide_feedback()
                        setup_game()
                    elif event.key == K_h:
                        difficulty = 'hard'
                        targetCount = 60 * 3  # 每种图片60次，共3种
                        intro = False
                        provide_feedback()
                        setup_game()
                elif gameOver:
                    if event.key == K_r:
                        totalScore = 0
                        score = 0
                        itemCount = 5
                        intro = True
                        gameOver = False
                        winCount = 0
                        countdown = 300  # 重置倒计时
                        startTime = pygame.time.get_ticks()  # 重置开始时间
                        setup_game()
                    elif event.key == K_q:
                        pygame.quit()
                        exit()
            elif event.type == MOUSEBUTTONUP and not intro and not gameOver:
                handle_click(event, offsetX, offsetY, score, totalScore, itemCount)

        current_time = pygame.time.get_ticks()  # 获取当前时间
        if not intro and not gameOver:
            if startTime is None:
                startTime = current_time
            elif (current_time - startTime) // 1000 > countdown:
                gameOver = True
                countdown = 300  # 重置倒计时

        draw_game_state(playSurface, intro, gameOver, font, largeFont, totalScore, offsetX, offsetY, startTime)
        # 绘制边框
        draw_border(playSurface, blackColor, 5)
        if not gameOver and not intro:
            if winCount >= targetCount:
                draw_victory_screen(playSurface, largeFont, font)

        pygame.display.update()
        fpsClock.tick(30)

def setup_game():
    global data, store, winCount
    itemCount = 3 if difficulty == 'easy' else 9
    data = [[randint(1, itemCount) for _ in range(3)] for _ in range(3)]
    for i in range(3):
        shuffle(data[i])
    store = [0] * 7
    winCount = 0  # 重置胜利计数器

def handle_click(event, offsetX, offsetY, score, totalScore, itemCount):
    global gameOver, winCount
    (x, y) = event.pos
    msg = Point(x, y)
    for r in range(3):
        for c in range(3):
            x = offsetX + c * (icoSize + 48)
            y = offsetY + r * (icoSize + 48)
            if (msg.x > x and msg.x < x + icoSize and msg.y > y and msg.y < y + icoSize):
                col = c
                row = r
                clicked = False
                for i in range(7):
                    if store[i] == 0:
                        store[i] = data[row][col]
                        clicked = True
                        provide_feedback()  # 播放点击音效
                        break
                if clicked and len([item for item in store if item != 0]) == 7 and all(count < 3 for count in [store.count(item) for item in store if item != 0]):
                    gameOver = True
                    return
                if clicked:
                    count = store.count(data[row][col])
                    if count == 3:
                        for i in range(7):
                            if store[i] == data[row][col]:
                                store[i] = 0
                        score += 1
                        totalScore += 1
                        if score >= itemCount:
                            itemCount += 1
                            score = 0
                    data[row][col] = randint(1, itemCount)
                return
    if not gameOver:
        winCount += 1  # 增加胜利计数器

def draw_game_state(playSurface, intro, gameOver, font, largeFont, totalScore, offsetX, offsetY, startTime):
    if intro:
        draw_intro_screen(playSurface, largeFont, font)
    elif gameOver:
        draw_game_over_screen(playSurface, largeFont, font, totalScore)
    else:
        playSurface.fill(whiteColor)
        color = (255, 0, 0)
        text = font.render("Mission: " + str(itemCount), True, color)
        playSurface.blit(text, (5, 45))
        color = (0, 255, 0)
        text = font.render("Score: " + str(totalScore), True, color)
        playSurface.blit(text, (5, 65))

        if startTime is not None:
            time_elapsed = (pygame.time.get_ticks() - startTime) // 1000
            remaining_time = countdown - time_elapsed
            if remaining_time >= 0:
                text = font.render(f"Time: {remaining_time}", True, blueColor)
                playSurface.blit(text, (5, 85))
            else:
                text = font.render("Time's Up!", True, redColor)
                playSurface.blit(text, (5, 85))

        for r in range(3):
            for c in range(3):
                if data[r][c]:
                    playSurface.blit(sheepImages[data[r][c] - 1], (offsetX + c * (icoSize + 48), offsetY + r * (icoSize + 48)))
        for i, color in enumerate(store):
            if color:
                playSurface.blit(sheepImages[color - 1], (i * 50 + 26, 620))

if __name__ == "__main__":
    main()