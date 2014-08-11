<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" omit-xml-declaration="yes" indent="no" />
<xsl:template match="/">
<xsl:for-each select="//table">SPIELTAG
<xsl:for-each select="tr[contains(@class, 'bundesliga_overview_row')]">
<xsl:value-of select="td[1]"/><xsl:text>	</xsl:text><xsl:value-of select="td[2]"/><xsl:text>	-	</xsl:text><xsl:value-of select="td[3]"/><xsl:text>
</xsl:text>
</xsl:for-each>
</xsl:for-each>
</xsl:template>
</xsl:stylesheet>

