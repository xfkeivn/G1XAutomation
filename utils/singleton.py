class Singleton(type):
  _instances = {}
  def __call__(class_, *args, **kwargs):
    if class_ not in class_._instances:
        class_._instances[class_] = super(Singleton, class_).__call__(*args, **kwargs)
    return class_._instances[class_]