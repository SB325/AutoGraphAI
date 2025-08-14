from neo4j_graphrag.experimental.pipeline import Component, DataModel
from neo4j_graphrag.experimental.pipeline import Pipeline
import asyncio
import webbrowser

class IntResultModel(DataModel):
    result: int

# Example component method that performs a task. 
class component_task(Component):
    async def run(self, number1: int, number2: int = 1) -> IntResultModel:
        return IntResultModel(result = number1 + number2)

class KG_Pipeline():
    def __init__(self):
        self.pipe = Pipeline()
    
    def add_component(self, component_task, task_label: str):
        self.pipe.add_component(component_task(), task_label)

    def connect_tasks(self, first_task_label: str, second_task_label: str):
        self.pipe.connect(
            first_task_label, 
            second_task_label, 
            input_config={"number2": "first_task_label.result"}
        )

    def run_dag(self):
        output = asyncio.run(self.pipe.run({"a": {"number1": 10, "number2": 1}, "b": {"number1": 4}}))
        # result: 10+1+4 = 15
        result output

    def save_pipeline_to_img_file(self, 
            filename, 
            show_in_browser: bool = False,
            hide_unused_outputs: bool = False
            ):
        self.pipe.draw(filename, hide_unused_outputs=False)
        if show_in_browser:
            webbrowser.open(filename)