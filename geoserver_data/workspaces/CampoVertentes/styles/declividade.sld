<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>declividade-recortado</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="intervals">
              <sld:ColorMapEntry color="#fde4d9" quantity="3" label="Plano (0 - 3%)"/>
              <sld:ColorMapEntry color="#fdcab5" quantity="8" label="Suave-ondulado (3 - 8%)"/>
              <sld:ColorMapEntry color="#fc8f6f" quantity="20" label="Ondulado (8 - 20%)"/>
              <sld:ColorMapEntry color="#fc6b41" quantity="45" label="Forte-ondulado (20 - 45%)"/>
              <sld:ColorMapEntry color="#f43e27" quantity="75" label="Montanhoso (45 - 75%)"/>
              <sld:ColorMapEntry color="#bc2322" quantity="126" label="Forte-Montanhoso (> 75%)"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>