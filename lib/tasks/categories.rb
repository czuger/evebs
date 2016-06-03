namespace :data_setup do

  # Presumed dead code.
  # desc "Create a market group tree"
  # task :market_group_tree => :environment do
  #   puts 'About to read the categories '
  #
  #   s = SimpleSpreadsheet::Workbook.read('../work/invMarketGroup.xls')
  #   s.selected_sheet = s.sheets.first
  #   s.first_row.upto(s.last_row) do |line|
  #     market_group_id = s.cell(line, 1)
  #     data2 = s.cell(line, 3)
  #   end
  #
  #   blueprints_array=Blueprint.blueprints_array
  #   eve_item_hash=EveItem.download_items_hash
  #   blueprints_array.each do |bp|
  #     item_id = bp[:produced_item_id]
  #     unless EveItem.find_by_cpp_eve_item_id( item_id )
  #       item_name = eve_item_hash[item_id]
  #       if item_name
  #         puts "About to insert #{item_id}, #{item_name}"
  #         EveItem.find_or_create_by( cpp_eve_item_id: item_id, name: item_name, name_lowcase: item_name.downcase )
  #       end
  #     end
  #   end
  # end
  # desc "Fill name_lowcase"
  # task :fill_name_lowcase => :environment do
  #   EveItem.all.to_a.each do |ei|
  #     puts "About to lowercase #{ei.name}"
  #     ei.update_attribute( :name_lowcase, ei.name.downcase )
  #   end
  # end

end