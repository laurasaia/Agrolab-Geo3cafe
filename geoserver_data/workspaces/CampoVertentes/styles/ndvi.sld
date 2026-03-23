<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:sld="http://www.opengis.net/sld">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>NDVI</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="intervals">
              <sld:ColorMapEntry color="#d7191c" quantity="0.20000000000000001" label="&lt;= 0,2"/>
              <sld:ColorMapEntry color="#fdae61" quantity="0.40000000000000002" label="0,2 - 0,4"/>
              <sld:ColorMapEntry color="#ffffc0" quantity="0.59999999999999998" label="0,4 - 0,6"/>
              <sld:ColorMapEntry color="#a6d96a" quantity="0.80000000000000004" label="0,6 - 0,8"/>
              <sld:ColorMapEntry color="#1a9641" quantity="1.10000000000000000" label="> 0,8"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>