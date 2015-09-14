class Crest::ComputePriceHistoryAvg

  def initialize()

    ActiveRecord::Base.transaction do

      last_month = Date.today - 1.month

      sql = "
      INSERT INTO dev.crest_prices_last_month_averages
        SELECT region_id, eve_item_id, SUM( order_count ), SUM( volume ), AVG( order_count ), AVG( volume ),
          AVG( low_price ), AVG( avg_price ), AVG( high_price ), now(), now()
        FROM dev.crest_price_histories
        WHERE history_date > '#{last_month}' AND
              NOT EXISTS (
                  SELECT region_id, eve_item_id
                  FROM dev.crest_prices_last_month_averages
                  WHERE dev.crest_prices_last_month_averages.region_id = dev.crest_price_histories.region_id
                  AND dev.crest_prices_last_month_averages.eve_item_id = dev.crest_price_histories.eve_item_id  )
        GROUP BY region_id, eve_item_id
      "
      ActiveRecord::Base.connection.execute(sql)

      sql = "
        UPDATE crest_prices_last_month_averages SET
          order_count_sum = sub.order_count_sum,
          volume_sum = sub.volume_sum,
          order_count_avg = sub.order_count_avg,
          volume_avg = sub.volume_avg,
          low_price_avg = sub.low_price_avg,
          avg_price_avg = sub.avg_price_avg,
          high_price_avg = sub.high_price_avg,
          updated_at = now()
        FROM ( SELECT
          region_id, eve_item_id,
          SUM( order_count ) order_count_sum, SUM( volume ) volume_sum,
          AVG( order_count ) order_count_avg, AVG( volume ) volume_avg,
          AVG( low_price ) low_price_avg, AVG( avg_price ) avg_price_avg, AVG( high_price ) high_price_avg
          FROM crest_price_histories
          WHERE history_date > '2015-08-11'
          GROUP BY region_id, eve_item_id ) sub
        WHERE crest_prices_last_month_averages.region_id = sub.region_id
        AND crest_prices_last_month_averages.eve_item_id = sub.eve_item_id;
      "
      ActiveRecord::Base.connection.execute(sql)

    end
  end
end