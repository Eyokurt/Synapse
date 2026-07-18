
def setup(registry, bus):
    @registry.register
    def calculate_tax(amount: int) -> float:
        '''Verilen tutarin %20 vergisini hesaplar.'''
        return amount * 0.20
    