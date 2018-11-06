module ApplicationHelper

  def selected_link_class( class_string, path = root_path )
    class_string += ' active' if current_page?( path )
    class_string
  end

  def active_link( a, b = root_path )
    selected_link_class( a, b )
  end

  def simple_menu_link( menu_text, menu_link='#' )
    content_tag(:li, nil, { class: 'nav-item' } ) do
      link_to menu_text, menu_link, class: selected_link_class( 'nav-link', menu_link )
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

end
