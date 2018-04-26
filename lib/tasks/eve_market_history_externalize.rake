require 'fileutils'

namespace :data_management do
  desc 'Externalize eve_markets_histories data'
  task :externalize_eve_markets_histories => :environment do

  #   dt_min = EveMarketsHistory.minimum( :history_date )
  #   dt_min = DateTime.new( dt_min.year )
  #   dt_max = dt_min + 1.year
  #
  #   request = "
  #   INSERT INTO eve_market_history_archives SELECT
  #     region_id, eve_item_id, to_char( history_date, 'YYYY' ), to_char( history_date( 'MM' ), history_date, order_count,
  #     volume, low_price, avg_price, high_price, now(), now() FROM eve_markets_histories
  #     where history_date < now() - interval '2 months'
  #   "
  #     dt_min = dt_max
  #     dt_max = dt_min + 1.year
  #   end
  #
  #
  end
end