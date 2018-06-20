class Sql::PricesAvgWeeks

  def self.update
    ActiveRecord::Base.transaction do
      Banner.p 'About to update prices avg weeks'

      request = File.open( "#{Rails.root}/sql/update_prices_avg_weeks.sql" ).read
      ActiveRecord::Base.connection.execute( request )
    end
  end

end