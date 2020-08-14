<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0"
                       xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"
                       xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
                       xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name></Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <Name>districts</Name>
          <Title>
            districts
            <Localized lang="de">Stadtbezirke</Localized>
            <Localized lang="en">City Districts</Localized>
          </Title>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#AAAAAA66</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#707070</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
      <FeatureTypeStyle>
        <Rule>
          <Name>mode_share</Name>
          <Title>
            mode_share
            <Localized lang="de">Stadtbezirke</Localized>
            <Localized lang="en">City Districts</Localized>
          </Title>
          <PointSymbolizer>
            <Geometry>
              <ogc:Function name="centroid">
                <ogc:PropertyName>geom</ogc:PropertyName>
              </ogc:Function>
            </Geometry>
            <Graphic>
              <ExternalGraphic>
                <OnlineResource
                                xlink:href="http://chart?cht=p&amp;chd=t:${share_foot},${share_bike},${share_mivd},${share_mivp},${share_put}&amp;chp=0.2&amp;chf=bg,s,0000FF00&amp;chco=00a6ff,20a849,c43114,f29305,1455e0" />
                <Format>application/chart</Format>
              </ExternalGraphic>
              <Size>
                <ogc:Add>
                  <ogc:Literal>50</ogc:Literal>
                  <ogc:Mul>
                    <ogc:Div>
                      <ogc:PropertyName>share_foot</ogc:PropertyName>
                      <ogc:Literal>20000000.0</ogc:Literal>
                    </ogc:Div>
                    <ogc:Literal>60</ogc:Literal>
                  </ogc:Mul>
                </ogc:Add>
              </Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>     
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>