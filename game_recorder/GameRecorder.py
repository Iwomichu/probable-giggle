import numpy as np
import cv2
import torch

from typing import List

from game_recorder.Frame import Frame
from constants import RECORDED_GAMES_DIRECTORY


class GameRecorder:
    def __init__(
            self,
            screen_width: int,
            screen_height: int,
            grayscale: bool = False,
            directory: str = "test",
            filename: str = "test",
            frame_length: int = 1
    ):
        self.frames: List[Frame] = []
        recordings_directory = RECORDED_GAMES_DIRECTORY / directory
        recordings_directory.mkdir(exist_ok=True)
        self.filepath = recordings_directory / f"{filename}.mp4"
        self.frame_length = frame_length
        self.width = screen_width
        self.height = screen_height
        self.grayscale = grayscale

    def add_frame(self, frame_raw: np.ndarray) -> None:
        frame_width, frame_height, n_channels = frame_raw.shape
        assert frame_width == self.width
        assert frame_height == self.height
        if self.grayscale:
            assert n_channels == 1
            frame_raw = frame_raw.squeeze(-1)
        else:
            assert n_channels == 3
        self.frames.append(Frame(frame_raw, self.frame_length))

    def add_torch_frame(self, frame_torch: torch.Tensor) -> None:
        self.add_frame(frame_torch.transpose(2, 0).numpy())

    def save_recording(self) -> None:
        fps = 20
        out = cv2.VideoWriter(str(self.filepath.absolute()), cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.width, self.height), not self.grayscale)
        for frame in self.frames:
            for i in range(frame.duration):
                out.write(frame.screen.astype(np.uint8))
