import pytest
from src.app.utils.learning_program import LearningProgram

lp = LearningProgram()


@pytest.mark.parametrize("level, level_data", lp.levels.items())
def test_level_data(level, level_data):
    letters = set(level_data.get("letters",[]))
    new_letters = set(level_data.get("new_letters",[]))
    if not letters: return
    if words:=level_data.get("words",[]):
        for w in words:
            assert set(w).issubset(letters) == True
            assert set(w) & new_letters
    if phrases:=level_data.get("phrases",[]):
        letters.add(' ')
        for ph in phrases:
            assert set(ph).issubset(letters) == True
            assert set(ph) & new_letters
