# tetris_core.py
import random

# --- 全局常量  ---
S_WIDTH = 950
S_HEIGHT = 700
PLAY_WIDTH = 300
PLAY_HEIGHT = 600
BLOCK_SIZE = 30
TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT

BG_COLOR = (10, 10, 45)
GRID_COLOR = (40, 40, 80)
BORDER_COLOR = (255, 255, 255)
SHAPE_COLORS = [
    (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0),
    (255, 165, 0), (0, 0, 255), (128, 0, 128)
]

S = [['.....', '.....', '..00.', '.00..', '.....'],
     ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'],
     ['.....', '..0..', '.00..', '.0...', '.....']]
I = [['..0..', '..0..', '..0..', '..0..', '.....'],
     ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'],
     ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'],
     ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'],
     ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'],
     ['.....', '.00..', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'],
     ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'],
     ['.....', '..0..', '.00..', '..0..', '.....']]

SHAPES = [S, Z, I, O, J, L, T]

# --- 核心类 ---
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

# --- 通用工具函数 ---
def create_grid(locked_positions={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        if x < 0 or x >= 10: return False
        if pos not in accepted_pos:
            if y > -1: return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1: return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

# --- 消除与下落算法 🔥 ---
def clear_rows(grid, locked):
    """
    清除满行并精确处理上方方块的下落。
    """
    # 1. 先找出所有满行的行号（y坐标）
    full_rows = []
    for y in range(len(grid)):
        # 如果一行中没有黑色(0,0,0)格子，说明满了
        if (0,0,0) not in grid[y]:
            full_rows.append(y)
            
    cleared_count = len(full_rows)
    if cleared_count == 0:
        return 0
        
    # 2. 从 locked 数据中彻底删除这些满行的所有方块
    for y in full_rows:
        for x in range(10):
            if (x, y) in locked:
                del locked[(x, y)]
                
    # 3. 精确计算剩余方块的新位置
    # 我们创建一个新的字典来存储下落后的位置，避免在遍历时修改字典导致数据错乱
    new_locked = {}
    
    # 遍历原来的 locked 中剩下的每一个方块
    for (x, y), color in locked.items():
        # 关键：计算这个方块下面有几行被消除了
        rows_below_cleared = 0
        for full_row_y in full_rows:
            if full_row_y > y: # 如果满行在当前方块下方
                rows_below_cleared += 1
        
        # 新的 y 坐标 = 原来的 y + 下面被消除的行数
        new_y = y + rows_below_cleared
        # 将方块存入新的位置
        new_locked[(x, new_y)] = color
        
    # 4. 用新的字典替换旧的字典，完成状态更新
    locked.clear()
    locked.update(new_locked)
    
    return cleared_count