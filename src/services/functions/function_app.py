import azure.functions as func
from example1.function import bp_1
from example2.function import bp_2

# Define the main app
app = func.FunctionApp()

# Register all the Blueprint apps
bps = [bp_1, bp_2]
for bp in bps:
    app.register_functions(bp)