module ApplicationHelper

  def selected_link_class( class_string, path = root_path )
    class_string += ' active' if current_page?( path )
    class_string
  end

  def active_link( a, b = root_path )
    selected_link_class( a, b )
  end

  def simple_menu_link( menu_text, menu_link='#', options= {} )
    content_tag(:li, nil, { class: 'nav-item' } ) do
      link_to menu_text, menu_link, options.merge( class: selected_link_class( 'nav-link', menu_link ) )
    end
  end

  def dropdown_menu_block( menu_text, menu_link='#' )
    menu_key = menu_text + 'Dropdown'
    content_tag(:li, nil, { class: 'nav-item dropdown' } ) do
      c = link_to menu_text, menu_link, class: 'nav-link dropdown-toggle', 'data-toggle' => 'dropdown',
            role: 'button', 'aria-haspopup' => true, 'aria-expanded' => false, id: menu_key
      c += content_tag( :div, nil,{ class: 'dropdown-menu', 'aria-labelledby' => menu_key } ) do
        yield
      end
      c
    end
  end

  def dropdown_sub_menu_link( menu_text, menu_link='#', in_new_window=false )
    # link_to 'Items tree', edit_choose_items_path, class: active_link( 'dropdown-item', edit_choose_items_path )
    if in_new_window
      link_to menu_text, menu_link, class: selected_link_class( 'dropdown-item', menu_link ), target: '_blank'
    else
      link_to menu_text, menu_link, class: selected_link_class( 'dropdown-item', menu_link )
    end
  end

  def help_tooltip( tt_code )
    fa_icon 'question-circle', 'data-toggle' => 'tooltip', title: t( '.tooltips.' + tt_code.to_s )
  end

  def help_tooltip_with_link( tt_code, link )
    link_to link do
      fa_icon 'question-circle', 'data-toggle' => 'tooltip', title: t( '.tooltips.' + tt_code.to_s )
    end
  end

  def filter_icon( data )
    fa_icon :filter if data
  end

  def safe_multiply( a, b )
    return Float::INFINITY unless a && b
    a * b
  end

  def show_last_update
    if @last_update_type
      last_update = Misc::LastUpdate.where( update_type: @last_update_type ).first&.updated_at

      if last_update
        current_date = Time.now.to_date
        last_update_date = last_update.to_date

        if last_update_date == current_date
          date_string = 'today at '
        elsif last_update_date == current_date - 1
          date_string = 'yesterday at '
        else
          date_string = "#{((Time.now - last_update)/(3600*24)).floor} days ago at "
        end

        last_update_string = date_string + last_update.hour.to_s

        "Last update : #{last_update.to_s} (#{last_update_string})"
      end

    end
  end

	# Meta and SOE

	def meta_title_helper
		( @meta_title || @title || 'EveBusinessServer (Beta)' ) + ' - EVE Online market information'
	end

  def meta_content
    @meta_content || 'Eve business server is a tool that show potential earnings in Eve Online'
  end

  def build_soe_data

    if controller_name == 'items'
			md = Metadata::Item.new
			md.add(@item, item_url( @item.id ) )
		elsif
			md = Metadata::WebPage.new( meta_title_helper, meta_content, @last_update_type )
		end

		if %w( items list_items ).include?( controller_name )
			md.add_breadcrumb( breadcrumb ) do |id|
				list_items_url( id ? {group_id: id} : nil )
			end
		end

    md.to_json
  end

end
