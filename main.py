import json
import io

import quart
import quart_cors
from quart import request
import matplotlib.pyplot as plt

app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

# Keep track of expenses. Does not persist if Python session is restarted.
_EXPENSES = {}


@app.post("/expenses/<string:username>")
async def add_expense(username):
    request_data = await quart.request.get_json(force=True)
    if username not in _EXPENSES:
        _EXPENSES[username] = []
    _EXPENSES[username].append(request_data["expense"])
    return quart.Response(response='OK', status=200)


@app.get("/expenses/<string:username>")
async def get_expenses(username):
    return quart.Response(response=json.dumps(_EXPENSES.get(username, [])), status=200)


@app.delete("/expenses/<string:username>")
async def delete_expense(username):
    request_data = await quart.request.get_json(force=True)
    expense_id = request_data["expense_id"]
    # fail silently, it's a simple plugin
    if 0 <= expense_id < len(_EXPENSES[username]):
        _EXPENSES[username].pop(expense_id)
    return quart.Response(response='OK', status=200)


@app.get("/expenses/<string:username>/pie_chart")
async def get_pie_chart(username):
    categories = {}
    for expense in _EXPENSES.get(username, []):
        categories[expense["category"]] = categories.get(
            expense["category"], 0) + expense["amount"]
    fig, ax = plt.subplots()
    ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
    ax.axis('equal')
    file_name = "./pie_chart/"
    plt.rcParams['font.sans-serif'] = ['Kaitt', 'SimHei']
    plt.savefig(file_name+"buf.png")
    return quart.Response(response="<img src='https://w16et2-5003.csb.app/pie_chart/buf.png'></img>", status=200)

    # return await quart.send_file(buf, mimetype='image/png', as_attachment=False)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/pie_chart/buf.png")
async def plugin_buf():
    filename = './pie_chart/buf.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
