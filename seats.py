import seatsio
client = seatsio.Client(seatsio.Region.OC(), secret_key="906ca45f-f584-4a65-9392-220b268543da")


def create_chart():
    chart = client.charts.create(
    )
    return chart
    
def create_seatsio_event(chart):
    event = client.events.create(chart.key, event_key= "my_Event")
    return event

def list_charts():
    charts = client.charts.list()
    for chart in charts:
        print("Chart: " + chart.name +  " " + chart.key)
        
def list_events():
    client.events.list()