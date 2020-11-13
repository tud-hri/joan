import abc


class SharedVariables(abc.ABC):

    def get_all_properties(self):
        all_properties = []
        for attribute in dir(type(self)):
            if type(getattr(type(self), attribute)) == property:
                all_properties.append(attribute)

        return all_properties

