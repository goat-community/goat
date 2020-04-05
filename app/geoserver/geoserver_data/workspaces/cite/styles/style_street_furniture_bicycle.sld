<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <Name>street_furniture_bicycle</Name>
    <UserStyle>
      <Name>furniture_bicycles</Name>
      <Title>Style Bicycle Parking</Title>
      <Abstract>Category styling for Cycling Furniture</Abstract>

      <FeatureTypeStyle>
        <Rule>
          <Title>bicycle_parking</Title>
          <MaxScaleDenominator>80000</MaxScaleDenominator>
          <PointSymbolizer>
            <Graphic>
              <ExternalGraphic>
             
                <OnlineResource xlink:type="simple" xlink:href="street_furniture_bicycle/${strToLowerCase(amenity)}.png" />
                <Format>image/png</Format>
              </ExternalGraphic>
            <Size>
                <ogc:Literal>22</ogc:Literal>
            </Size>
            </Graphic>
         
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>