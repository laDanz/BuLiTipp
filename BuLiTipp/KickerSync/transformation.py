transformation='''<?xml version="1.0"?>
<!-- for page http://www.kicker.de/news/fussball/bundesliga/spieltag/1-bundesliga/2014-15/13/0/spieltag.html -->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" encoding="utf-8" />
	
	<xsl:template match="/">
		<xsl:apply-templates />
	</xsl:template>
	
	<xsl:template match="*[local-name()='table']">
		<xsl:if test="contains(@class, 'tab1-bundesliga')">
			<spieltag>
				<xsl:apply-templates/>
			</spieltag>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="*[local-name()='tr']">
	<!--xsl:for-each select="//tr[contains(@class, 'fest')]"-->
		<xsl:if test="contains(@class, 'fest')">
			<spiel>
				<!--first td is day of week -->
				<!-- second is date like 28.11. 20:30, or nothing, which means previous -->
				<zeitpunkt format="%d.%m. %H:%M">
					<xsl:call-template name="lastZeitpunkt">
						<xsl:with-param name="spiel" select="." />
					</xsl:call-template>
				</zeitpunkt>
				<!-- third is home team -->
				<heimmannschaft>
					<xsl:value-of select="normalize-space(*[local-name()='td'][3])"/>
				</heimmannschaft>
				<!-- 4th is splitting character -->
				<!-- 5th is away team -->
				<auswmannschaft>
					<xsl:value-of select="normalize-space(*[local-name()='td'][5])"/>
				</auswmannschaft>
				<!-- 6th is result: 1:4 (1:1) or  -:- (-:-) -->
				<ergebnis>
					<xsl:choose>
						<xsl:when test="contains(*[local-name()='td'][6], '-:-')">
							<xsl:text>DNF</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="substring-before(normalize-space(*[local-name()='td'][6]), ' ')"/>
						</xsl:otherwise>
					</xsl:choose>
				</ergebnis>
			</spiel>
		</xsl:if>
	<!--/xsl:for-each-->
	</xsl:template>
	
	<xsl:template name="lastZeitpunkt">
	<!-- Template, that looks over the last <tr>s to find the last zeitpunkt -->
		<xsl:param name="spiel" />
		<xsl:param name="count" select="count((preceding-sibling::*[local-name()='tr' and contains(@class, 'fest')]))" />
		<xsl:choose>
			<xsl:when test="normalize-space($spiel/*[local-name()='td'][2])">
				<xsl:value-of select="normalize-space($spiel/*[local-name()='td'][2])"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="lastZeitpunkt">
					<xsl:with-param name="spiel" select="(preceding-sibling::*[local-name()='tr' and contains(@class, 'fest')])[$count]" />
					<xsl:with-param name="count" select="$count - 1" />
				</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="*">
	<!-- match all element, to avoid unwanted output -->
		<!-- WARNING: Unmatched element: <xsl:value-of select="name()"/> -->
		<xsl:apply-templates/>
	</xsl:template>
	
	<xsl:template match="text()|@*">
	<!-- match all text nodes, to avoid unwanted output -->
		<!--xsl:value-of select="."/-->
	</xsl:template>
</xsl:stylesheet>'''