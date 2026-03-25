import torch, random, numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from helper import plot
MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001
class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    def get_state(self, game):
        head = game.snake[0]
        p_l = Point(head.x - BLOCK_SIZE, head.y)
        p_r = Point(head.x + BLOCK_SIZE, head.y)
        p_u = Point(head.x, head.y - BLOCK_SIZE)
        p_d = Point(head.x, head.y + BLOCK_SIZE)
        d_l = game.direction == Direction.LEFT
        d_r = game.direction == Direction.RIGHT
        d_u = game.direction == Direction.UP
        d_d = game.direction == Direction.DOWN
        state = [
            # Danger straight
            (d_r and game.is_collision(p_r)) or (d_l and game.is_collision(p_l)) or (
                        d_u and game.is_collision(p_u)) or (d_d and game.is_collision(p_d)),
            # Danger right
            (d_u and game.is_collision(p_r)) or (d_d and game.is_collision(p_l)) or (
                        d_l and game.is_collision(p_u)) or (d_r and game.is_collision(p_d)),
            # Danger left
            (d_d and game.is_collision(p_r)) or (d_u and game.is_collision(p_l)) or (
                        d_r and game.is_collision(p_u)) or (d_l and game.is_collision(p_d)),
            d_l,
            d_r,
            d_u,
            d_d,
            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]
        return np.array(state, dtype=int)
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            final_move[random.randint(0, 2)] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)
        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save()
            print(f'Game {agent.n_games} Score {score} Record {record}')
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
if __name__ == '__main__':
    train()