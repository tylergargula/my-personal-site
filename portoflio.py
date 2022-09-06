class Portfolio:
    def __init__(self, portfolio_id, portfolio_url, title, subtitle, tagline, image, body, cms,
                 urls_migrated, services, industry):
        self.id = portfolio_id
        self.url = portfolio_url
        self.title = title
        self.subtitle = subtitle
        self.tagline = tagline
        self.image = image
        self.body = body
        self.cms = cms
        self.urls_migrated = urls_migrated
        self.services = services
        self.industry = industry
