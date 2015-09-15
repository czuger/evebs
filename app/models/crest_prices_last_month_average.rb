class CrestPricesLastMonthAverage < ActiveRecord::Base
  belongs_to :region
  belongs_to :eve_item
end