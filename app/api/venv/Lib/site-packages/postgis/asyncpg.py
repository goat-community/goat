from .geometry import Geometry


async def register(connection):

    def encoder(value):
        if not isinstance(value, Geometry):
            raise ValueError('Geometry value must subclass Geometry class')
        return value.to_ewkb()

    def decoder(value):
        return Geometry.from_ewkb(value)

    await connection.set_type_codec(
        'geography', encoder=encoder, decoder=decoder)
    await connection.set_type_codec(
        'geometry', encoder=encoder, decoder=decoder)
