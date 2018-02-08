broker_url = 'pyamqp://'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Calcutta'

imports = ('squad_pantry_app.tasks',)

task_annotations= {
    'tasks.throughput': {'rate_limit': '1/d'}
}