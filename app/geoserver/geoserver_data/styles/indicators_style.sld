<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>indicators</Name>
    <UserStyle>
      <Name>indicators</Name>
      <Title>indicators</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>Very Good (score 80 - 100)</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>80</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>100</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">
                    <ogc:Function name="Interpolate">
        			 <ogc:PropertyName>sum_total</ogc:PropertyName>
                     <ogc:Literal>80</ogc:Literal>
                     <ogc:Literal>#659843</ogc:Literal>
                     <ogc:Literal>100</ogc:Literal>
                     <ogc:Literal>#385723</ogc:Literal>
         			<ogc:Literal>color</ogc:Literal>
                 </ogc:Function>
              </CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>Good (score 60 - 80)</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThan>
                <PropertyName>sum_total</PropertyName>
                <Literal>60</Literal>
              </PropertyIsGreaterThan>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>80</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">
                    <ogc:Function name="Interpolate">
        			 <ogc:PropertyName>sum_total</ogc:PropertyName>
                     <ogc:Literal>60</ogc:Literal>
                     <ogc:Literal>#a0bf3c</ogc:Literal>
                     <ogc:Literal>80</ogc:Literal>
                     <ogc:Literal>#61953d</ogc:Literal>
         			<ogc:Literal>color</ogc:Literal>
                 </ogc:Function>
              </CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>Medium (score 40 - 60)</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThan>
                <PropertyName>sum_total</PropertyName>
                <Literal>40</Literal>
              </PropertyIsGreaterThan>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>60</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <LineSymbolizer>
            <Stroke>
                <CssParameter name="stroke">
                    <ogc:Function name="Interpolate">
        			 <ogc:PropertyName>sum_total</ogc:PropertyName>
                     <ogc:Literal>40</ogc:Literal>
                     <ogc:Literal>#fec107</ogc:Literal>
                     <ogc:Literal>60</ogc:Literal>
                     <ogc:Literal>#9fbe36</ogc:Literal>
         			<ogc:Literal>color</ogc:Literal>
                 </ogc:Function>
              </CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>Bad (score 20 - 40)</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThan>
                <PropertyName>sum_total</PropertyName>
                <Literal>20</Literal>
              </PropertyIsGreaterThan>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>40</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <LineSymbolizer>
            <Stroke>
             <CssParameter name="stroke">
                    <ogc:Function name="Interpolate">
        			 <ogc:PropertyName>sum_total</ogc:PropertyName>
                     <ogc:Literal>20</ogc:Literal>
                     <ogc:Literal>#ed8137</ogc:Literal>
                     <ogc:Literal>40</ogc:Literal>
                     <ogc:Literal>#ed8137</ogc:Literal>
         			<ogc:Literal>color</ogc:Literal>
                 </ogc:Function>
              </CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
        <Rule>
          <Name>Very Bad (score 0 - 20)</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThan>
                <PropertyName>sum_total</PropertyName>
                <Literal>0</Literal>
              </PropertyIsGreaterThan>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>sum_total</PropertyName>
                <Literal>20</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <LineSymbolizer>
            <Stroke>
             <CssParameter name="stroke">
                    <ogc:Function name="Interpolate">
        			 <ogc:PropertyName>sum_total</ogc:PropertyName>
                     <ogc:Literal>0</ogc:Literal>
                     <ogc:Literal>#c10707</ogc:Literal>
                     <ogc:Literal>20</ogc:Literal>
                     <ogc:Literal>#be987f</ogc:Literal>
         			<ogc:Literal>color</ogc:Literal>
                 </ogc:Function>
              </CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
              <CssParameter name="stroke-linecap">square</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>