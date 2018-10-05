class ComponentsToBuy < ApplicationRecord
  belongs_to :user
  belongs_to :eve_item

  # def self.total_volume(components_to_buy)
  #   components_to_buy.map{ |e| e.quantity * e.eve_item.volume }.inject( &:+ )&.round(1)
  # end
  #
  # def self.total_isk(components_to_buy)
  #   components_to_buy.map{ |e| e.quantity * e.eve_item.cost }.inject( &:+ )
  # end

  def self.refresh_components_to_buy_list_for( user )

    items_to_buy = {}

    user.production_lists.where( 'runs_count > 0' ).each do |pl|
      runs_counts_array = []

      requested_run_counts = pl.runs_count
      blueprint = pl.eve_item.blueprint

      max_run_count_per_job = blueprint.nb_runs

      while requested_run_counts > 0
        if requested_run_counts <= max_run_count_per_job
          runs_counts_array << requested_run_counts
          requested_run_counts = 0
        else
          runs_counts_array << max_run_count_per_job
          requested_run_counts -= max_run_count_per_job
        end
      end

      runs_counts_array.each do |runs_count|
        ComponentsToBuysDetail.where( user_id: user.id, bp_id: blueprint.id ).each do |cbd|
          items_to_buy[cbd.mat_id] ||= 0
          items_to_buy[cbd.mat_id] += ( runs_count * cbd.required_qtt * cbd.bp_reduction ).ceil
        end
      end
    end

    ActiveRecord::Base.transaction do
      user.components_to_buys.clear
      items_to_buy.each do |item_id, amount|
        user.components_to_buys.create!( eve_item_id: item_id, quantity: amount )
      end
    end
  end

end
