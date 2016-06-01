<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msiggi="http://msiggi.de/Sportsdata/Webservices">
<xsl:output method="text" omit-xml-declaration="yes" indent="no" />
<xsl:template match="/">
<xsl:text>BEZEICHNER
</xsl:text>
<xsl:value-of select="//Matchdata[1]/msiggi:leagueName"/>
<xsl:text>
SAISONTIPPEND
</xsl:text>
<xsl:value-of select="//Matchdata[1]/msiggi:matchDateTime"/>
<xsl:text>
POKAL
true
</xsl:text>
<xsl:for-each select="//Matchdata">
<xsl:if test="count(preceding-sibling::Matchdata) &lt; 1 or preceding-sibling::Matchdata[1]/msiggi:groupOrderID != msiggi:groupOrderID">
<xsl:text>SPIELTAG</xsl:text>
"<xsl:value-of select="msiggi:groupName"/>"
</xsl:if>
<xsl:value-of select="msiggi:matchDateTime"/>
<xsl:text>	</xsl:text>
<xsl:value-of select="msiggi:nameTeam1"/>
<xsl:text>	-	</xsl:text>
<xsl:value-of select="msiggi:nameTeam2"/>
<xsl:text>
</xsl:text>
</xsl:for-each>
</xsl:template>
</xsl:stylesheet>