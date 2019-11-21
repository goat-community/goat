<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:se="http://www.opengis.net/se" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <se:Name>parking</se:Name>
    <UserStyle>
      <se:Name>parking</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>no data</se:Name>
          <se:Description>
            <se:Title>no data</se:Title>
          </se:Description>
          <!--Parser Error: syntax error, unexpected ELSE - Expression was: ELSE-->
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#999999</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>diagonal</se:Name>
          <se:Description>
            <se:Title>diagonal</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>diagonal</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#00c1ce</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>perpendicular</se:Name>
          <se:Description>
            <se:Title>perpendicular</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>perpendicular</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#009224</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>parallel</se:Name>
          <se:Description>
            <se:Title>parallel</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>parallel</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#4fd234</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>marked</se:Name>
          <se:Description>
            <se:Title>marked</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>marked</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#f3ff0a</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>no_parking</se:Name>
          <se:Description>
            <se:Title>no_parking</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>parking_lane</ogc:PropertyName>
                <ogc:Literal>no_parking</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>parking_lane</ogc:PropertyName>
                <ogc:Literal>no</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#ed605b</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>no_stopping</se:Name>
          <se:Description>
            <se:Title>no_stopping</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>no_stopping</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#ff0901</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>fire_lane</se:Name>
          <se:Description>
            <se:Title>fire_lane</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>parking_lane</ogc:PropertyName>
              <ogc:Literal>fire_lane</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#d901ff</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>