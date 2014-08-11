<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" omit-xml-declaration="yes" indent="no" />
<xsl:template match="/">SPIELTAG
<xsl:for-each select="//tbody">
<xsl:for-each select="tr[not(contains(@class, 'row-headline'))]">
<!--xsl:value-of select="td[contains(@class, 'column-date')]//a"/--><xsl:value-of select="td[contains(@class, 'column-date')]"/><xsl:text>	</xsl:text><xsl:value-of select="td[contains(@class, 'column-club')][1]//div[contains(@class, 'club-name')]"/><xsl:text>	-	</xsl:text><xsl:value-of select="td[contains(@class, 'column-club')][2]//div[contains(@class, 'club-name')]"/><xsl:text>
</xsl:text>
</xsl:for-each>
</xsl:for-each>
</xsl:template>
</xsl:stylesheet>

