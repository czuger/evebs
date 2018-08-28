class Sql::BuyOrdersAnalyticsUpdate

  def self.update
    ActiveRecord::Base.transaction do
      Banner.p 'About to update buy_orders_analytics'

      request = File.open( "#{Rails.root}/sql/update_buy_ordrers_analytics.sql" ).read
      ActiveRecord::Base.connection.execute( request )
    end
  end

end