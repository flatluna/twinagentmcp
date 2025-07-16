from autogen_core.models import ModelFamily
print("Available ModelFamily attributes:")
print([attr for attr in dir(ModelFamily) if not attr.startswith('_')])
