# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "${var.app_name}-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    path                = "/health"
    matcher             = "200"
    port                = "traffic-port"
  }

  tags = {
    Name = "${var.app_name}-tg"
  }
}

# ALB Listener - HTTP
resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# HTTPS Listener (optional - requires SSL certificate)
# Uncomment and configure with your certificate ARN
# resource "aws_lb_listener" "app_https" {
#   load_balancer_arn = aws_lb.app.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
#   certificate_arn   = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERTIFICATE_ID"
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app.arn
#   }
# }
#
# # Redirect HTTP to HTTPS
# resource "aws_lb_listener_rule" "redirect_http_to_https" {
#   listener_arn = aws_lb_listener.app.arn
#
#   action {
#     type = "redirect"
#
#     redirect {
#       port        = "443"
#       protocol    = "HTTPS"
#       status_code = "HTTP_301"
#     }
#   }
#
#   condition {
#     path_pattern {
#       values = ["/*"]
#     }
#   }
# }
