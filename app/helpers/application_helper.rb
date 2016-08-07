module ApplicationHelper

  def active_link( path = root_path )
    'active' if current_page?( path )
  end

end
