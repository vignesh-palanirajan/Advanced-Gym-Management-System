 use  legacy_gym;
ALTER TABLE BRANCHES
ADD COLUMN MEMBER_COUNT INT DEFAULT 0;
ALTER TABLE BRANCHES
ADD COLUMN Trainer_count INT DEFAULT 0;

DELIMITER //

CREATE TRIGGER update_member_count_after_insert
AFTER INSERT ON MEMBERS
FOR EACH ROW
BEGIN
    UPDATE BRANCHES
    SET MEMBER_COUNT = MEMBER_COUNT + 1
    WHERE BRANCH_ID = NEW.BRANCH_ID;
END; //

CREATE TRIGGER update_member_count_after_delete
AFTER DELETE ON MEMBERS
FOR EACH ROW
BEGIN
    UPDATE BRANCHES
    SET MEMBER_COUNT = MEMBER_COUNT - 1
    WHERE BRANCH_ID = OLD.BRANCH_ID;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER update_trainer_count_after_insert
AFTER INSERT ON TRAINERS
FOR EACH ROW
BEGIN
    UPDATE BRANCHES
    SET TRAINER_COUNT = TRAINER_COUNT + 1
    WHERE BRANCH_ID = NEW.BRANCH_ID;
END; //

CREATE TRIGGER update_trainer_count_after_delete
AFTER DELETE ON TRAINERS
FOR EACH ROW
BEGIN
    UPDATE BRANCHES
    SET TRAINER_COUNT = TRAINER_COUNT - 1
    WHERE BRANCH_ID = OLD.BRANCH_ID;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER update_member_count_after_update
AFTER UPDATE ON MEMBERS
FOR EACH ROW
BEGIN
    -- Decrease count in the old branch if the branch ID has changed
    IF OLD.BRANCH_ID <> NEW.BRANCH_ID THEN
        UPDATE BRANCHES
        SET MEMBER_COUNT = MEMBER_COUNT - 1
        WHERE BRANCH_ID = OLD.BRANCH_ID;

        -- Increase count in the new branch
        UPDATE BRANCHES
        SET MEMBER_COUNT = MEMBER_COUNT + 1
        WHERE BRANCH_ID = NEW.BRANCH_ID;
    END IF;
END; //

DELIMITER ;
DELIMITER //

CREATE TRIGGER update_trainer_count_after_update
AFTER UPDATE ON TRAINERS
FOR EACH ROW
BEGIN
    -- Decrease count in the old branch if the branch ID has changed
    IF OLD.BRANCH_ID <> NEW.BRANCH_ID THEN
        UPDATE BRANCHES
        SET TRAINER_COUNT = TRAINER_COUNT - 1
        WHERE BRANCH_ID = OLD.BRANCH_ID;

        -- Increase count in the new branch
        UPDATE BRANCHES
        SET TRAINER_COUNT = TRAINER_COUNT + 1
        WHERE BRANCH_ID = NEW.BRANCH_ID;
    END IF;
END; //

DELIMITER ;