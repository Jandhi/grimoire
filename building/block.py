class Block:
    def __init__(self, name, properties) -> None:
        self.name = name
        self.properties = properties
    
    def __str__(self) -> str:
        string = self.name

        if len(self.properties) > 0:
            properties_string = ''

            for property in self.properties:
                properties_string += f',{property}={self.properties[property]}'

            string = f'{string}[{properties_string[1:]}]'
        
        return string