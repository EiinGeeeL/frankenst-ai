import azure.functions as func
from get_evolution_mcptool.function import bp_1
from indexer_pokeseriex_eventgrid.function import bp_2
from retriever_pokeseriex_mcptool.function import bp_3
# from example4.function import bp_4

# Define the main app
app = func.FunctionApp()

# Register all the Blueprint apps
bps = [bp_1, bp_2, bp_3, ]
for bp in bps:
    app.register_functions(bp)