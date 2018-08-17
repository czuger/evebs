module ApplicationHelper

  def active_link( class_string, path = root_path )
    class_string += ' active' if current_page?( path )
    class_string
  end

end
