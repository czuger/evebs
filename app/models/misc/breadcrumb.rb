module Misc
end

class Breadcrumb

	# def initialize( view_context, final_element )
	#
	# 	unless @breadcrumb
	# 		if final_element.parent_item
	# 			item = final_element.parent_item
	# 			ancestors = item.market_group.ancestors
	# 		elsif item.is_a?( EveItem )
	# 			item = final_element
	# 			ancestors = item.market_group.ancestors
	# 		else
	# 			item = final_element
	# 			ancestors = item.ancestors
	# 		end
	#
	# 		@breadcrumb = [ OpenStruct.new( name: 'Root', url: view_context.list_items_url ) ]
	#
	# 		@breadcrumb += final_element.breadcrumb_ancestors
	#
	#
	# 		OpenStruct.new( name: e.name, url: view_context.list_items_url( group_id: e.id ) )
	# 		end
	#
	#
	#
	# 			@breadcrumb << final_element.parent_items.to_breadcrumb_element
	# 			@breadcrumb << OpenStruct.new( name: @current_group.name, group_id: @current_group.id )
	# 		end
	#
	# 	end
	# 	@breadcrumb
	#
	# end


end