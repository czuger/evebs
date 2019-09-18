module Process
	class UpdateEveMarketHistoriesGroup

		def update
			Misc::Banner.p 'About to update eve_market_histories_group started'
			EveMarketHistoriesGroup.transaction do
				create_tmp_table
				transaction_update
			end

			Misc::Banner.p 'Update eve_market_histories_group finished'
		end

		def transaction_update
			from_file_to_tmp_table

			# TODO : on relance le processus horaire. Verifier si les données sont toujours dans la table
			p EveMarketHistoriesGroupTmpTable.where( 'cpp_region_id=10000030 and cpp_type_id=12775' ).first

			Sql::UpdateEveMarketHistoriesGroups.execute
			p EveMarketHistoriesGroup.where( 'eve_item_id=919 and universe_region_id = 28' ).first
		end

		private

		def from_file_to_tmp_table
			old_logger = ActiveRecord::Base.logger
			ActiveRecord::Base.logger = nil

			batch_inst = Libs::BatchBuffer.new( 'EveMarketHistoriesGroupTmpTable', :insert )

			1.upto(Esi::DownloadHistorySetProcessCount::PROCESSES_COUNT).each do |process_id|

				File.open( "data/regional_sales_volumes_#{process_id}.json_stream", 'r' ) do |f|
					f.each do |line|
						data = JSON.parse( line )

						batch_inst.add_data EveMarketHistoriesGroupTmpTable.new(
							cpp_type_id: data['cpp_type_id'], cpp_region_id: data['cpp_region_id'],
							volume: data['volume'], highest: data['max'], lowest: data['min'], average: data['avg'] )
					end
				end
			end

			batch_inst.flush_buffer

			ActiveRecord::Base.logger = old_logger
		end

		def create_tmp_table

			ActiveRecord::Migration.class_eval do
				create_table :eve_market_histories_group_tmp_tables, :temporary=> true do |t|
					t.integer :cpp_type_id, null: false
					t.integer :cpp_region_id, null: false

					t.bigint :volume, null: false

					t.float :lowest
					t.float :highest
					t.float :average
				end
			end

			# add_index :eve_market_histories_group_tmp_tables, [ :cpp_type_id, :cpp_region_id ], unique: true, name: :eve_market_histories_groups_cpp_index
		end

	end
end