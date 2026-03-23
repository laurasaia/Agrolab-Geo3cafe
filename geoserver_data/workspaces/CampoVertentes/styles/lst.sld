<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:sld="http://www.opengis.net/sld">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>BDC_LST_03-12-2025</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="intervals">
              <sld:ColorMapEntry color="#19b5f1" quantity="18" label="&lt;= 18&#176;"/>
              <sld:ColorMapEntry color="#23db3f" quantity="23" label="18&#176; - 23&#176;"/>
              <sld:ColorMapEntry color="#f3f01d" quantity="27" label="23&#176; - 27&#176;"/>
              <sld:ColorMapEntry color="#f57215" quantity="32" label="27&#176; - 32&#176;"/>
              <sld:ColorMapEntry color="#a4262c" quantity="60" label="> 32&#176;"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>