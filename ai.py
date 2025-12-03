# ai.py - 高性能优化版 (1.5步搜索)
from tetris_core import Piece, convert_shape_format, valid_space

# --- El-Tetris 评分权重  ---
WEIGHT_AGGREGATE_HEIGHT = -0.51
WEIGHT_COMPLETE_LINES   = 0.76
WEIGHT_HOLES            = -0.36
WEIGHT_BUMPINESS        = -0.18

def simulate_move(grid, piece, x, r):
    """
    模拟移动：返回 (是否合法, 模拟后的网格, 消除行数)
    """
    if x < -2 or x > 10: return False, None, 0

    temp_grid = [row[:] for row in grid]
    temp_piece = Piece(x, 0, piece.shape)
    temp_piece.rotation = r
    
    if not valid_space(temp_piece, grid): return False, None, 0
    
    # 硬降
    while valid_space(temp_piece, grid):
        temp_piece.y += 1
    temp_piece.y -= 1
    
    if temp_piece.y < 1: return False, None, 0

    # 写入网格
    shape_pos = convert_shape_format(temp_piece)
    for i in range(len(shape_pos)):
        px, py = shape_pos[i]
        if py > -1:
            temp_grid[py][px] = temp_piece.color
            
    # 计算消除
    cleared = 0
    for i in range(len(temp_grid)-1, -1, -1):
        if (0,0,0) not in temp_grid[i]:
            cleared += 1
            
    return True, temp_grid, cleared

def evaluate_grid(grid, cleared_rows):
    """评分函数 """
    aggregate_height = 0
    holes = 0
    bumpiness = 0
    column_heights = [0] * 10
    
    for x in range(10):
        for y in range(20):
            if grid[y][x] != (0,0,0):
                column_heights[x] = 20 - y
                break
    aggregate_height = sum(column_heights)
    
    for i in range(len(column_heights) - 1):
        bumpiness += abs(column_heights[i] - column_heights[i+1])
        
    for x in range(10):
        block_found = False
        for y in range(20):
            if grid[y][x] != (0,0,0):
                block_found = True
            elif block_found and grid[y][x] == (0,0,0):
                holes += 1

    score = (WEIGHT_AGGREGATE_HEIGHT * aggregate_height) + \
            (WEIGHT_HOLES * holes) + \
            (WEIGHT_BUMPINESS * bumpiness) + \
            (WEIGHT_COMPLETE_LINES * cleared_rows)
    return score

def get_best_move(grid, current_piece, next_piece=None):
    """
    优中选优策略
    """
    candidates = [] # 存储初选候选人
    curr_rotations = len(current_piece.shape)
    
    # --- 第一步：全面初选 ---
    for r1 in range(curr_rotations):
        for x1 in range(-2, 10):
            valid1, grid1, cleared1 = simulate_move(grid, current_piece, x1, r1)
            if valid1:
                # 计算基础分
                base_score = evaluate_grid(grid1, cleared1)
                # 将候选方案存下来：(分数, x, r, 模拟后的网格, 第一步消除数)
                candidates.append({'score': base_score, 'x': x1, 'r': r1, 'grid': grid1, 'cleared': cleared1})
    
    # 如果快死了，没路可选，就随便返回一个
    if not candidates:
        return (5, 0)

    # --- 第二步：筛选精英 ---
    # 按分数从高到低排序
    candidates.sort(key=lambda c: c['score'], reverse=True)
    
    # 只取前 6 名最好的去参加复试
    # 数字是性能和智商的平衡点，可以微调
    top_candidates = candidates[:6]
    
    best_score_final = -999999
    best_move_final = (candidates[0]['x'], candidates[0]['r']) # 默认选第一名的基础走法

    # --- 第三步：精英复试  ---
    if next_piece:
        next_rotations = len(next_piece.shape)
        for cand in top_candidates:
            max_score_layer2 = -999999
            has_valid_move_layer2 = False
            
            # 基于候选人的网格，尝试下一个方块的所有可能
            for r2 in range(next_rotations):
                for x2 in range(-2, 10):
                    valid2, grid2, cleared2 = simulate_move(cand['grid'], next_piece, x2, r2)
                    if valid2:
                        has_valid_move_layer2 = True
                        # 最终得分 = 两步走完后的局面分
                        s = evaluate_grid(grid2, cand['cleared'] + cleared2)
                        if s > max_score_layer2:
                            max_score_layer2 = s
            
            # 如果这一步走完，下一步有路可走，就用复试成绩更新总成绩
            if has_valid_move_layer2:
                if max_score_layer2 > best_score_final:
                    best_score_final = max_score_layer2
                    best_move_final = (cand['x'], cand['r'])
            # 如果下一步死棋了，这个候选人直接淘汰，不更新 best_move_final

    return best_move_final