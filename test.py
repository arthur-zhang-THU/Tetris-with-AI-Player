import unittest
import os
import sys

# 1. 强行设置为无显示模式 (必须在 import pygame 之前)
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

# --- 关键修改：从新的模块导入 ---
# 基础逻辑现在在 tetris_core 里
from tetris_core import create_grid, clear_rows, Piece, S, I, valid_space, S_WIDTH, S_HEIGHT
# AI 逻辑在 ai 里
import ai

class TestTetrisGame(unittest.TestCase):

    def setUp(self):
        """每个测试开始前运行"""
        pygame.init()
        pygame.font.init()
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        # 创建虚拟屏幕
        pygame.display.set_mode((S_WIDTH, S_HEIGHT))

    def tearDown(self):
        """每个测试结束后运行"""
        pygame.mixer.quit()
        pygame.display.quit()
        pygame.quit()

    # --- 基础逻辑测试 (Core) ---

    def test_grid_dimensions(self):
        print("\n[Core] 测试网格生成...", end="")
        locked_positions = {}
        grid = create_grid(locked_positions)
        self.assertEqual(len(grid), 20)
        self.assertEqual(len(grid[0]), 10)
        print("OK")

    def test_clear_rows(self):
        print("[Core] 测试消除行逻辑...", end="")
        locked_positions = {}
        # 填满第19行
        for x in range(10):
            locked_positions[(x, 19)] = (255, 0, 0)
        # 上方放一个
        locked_positions[(0, 18)] = (0, 255, 0)

        grid = create_grid(locked_positions)
        cleared = clear_rows(grid, locked_positions)

        self.assertEqual(cleared, 1)
        self.assertIn((0, 19), locked_positions)
        print("OK")

    def test_valid_space(self):
        print("[Core] 测试边界检测...", end="")
        locked_positions = {}
        grid = create_grid(locked_positions)
        
        piece = Piece(5, 5, S)
        self.assertTrue(valid_space(piece, grid))

        piece_out = Piece(-5, 5, S) # 左侧越界
        self.assertFalse(valid_space(piece_out, grid))
        
        piece_out_right = Piece(15, 5, S) # 右侧越界
        self.assertFalse(valid_space(piece_out_right, grid))
        print("OK")

    # --- AI 逻辑测试 (New) ---

    def test_ai_evaluation(self):
        print("[AI] 测试评分逻辑...", end="")
        # 场景 A: 一个完美的平地
        # 场景 B: 同样高度，但中间有个空洞
        
        locked_flat = {}
        locked_hole = {}
        
        # 造一个平地 (第19行全满)
        for x in range(10): locked_flat[(x, 19)] = (255,0,0)
        
        # 造一个有洞的 (第19行中间缺一个)
        for x in range(10): 
            if x != 5: locked_hole[(x, 19)] = (255,0,0)
            
        grid_flat = create_grid(locked_flat)
        grid_hole = create_grid(locked_hole)
        
        score_flat = ai.evaluate_grid(grid_flat)
        score_hole = ai.evaluate_grid(grid_hole)
        
        # AI 应该认为平地比有洞的分数高
        # 注意：因为 evaluate_grid 返回的是负数（惩罚分），所以数值越大越好（比如 -10 > -100）
        # 但在我们的算法里，空洞惩罚极重
        
        # 这里我们简单断言：平地的评分应该高于有洞的评分
        # 或者至少，有洞的评分应该包含惩罚
        
        self.assertTrue(score_flat > score_hole, f"AI应该更喜欢平地 (Flat: {score_flat}, Hole: {score_hole})")
        print("OK")

if __name__ == '__main__':
    print("开始运行全栈测试 (Core + AI)...")
    
    # 针对 Thonny 的手动加载模式
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTetrisGame)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    pygame.quit()
    print("测试结束。")
    
    sys.exit(not result.wasSuccessful())